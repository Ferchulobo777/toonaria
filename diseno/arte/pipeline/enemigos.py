"""Arma las animaciones de los enemigos, del jefe y de Ambrosio a partir de sus hojas.

Mismo criterio que `ventura.py`: cada hoja pasa por `pixelizar.py` y después se eligen y
ordenan los frames de cada animación del juego. Decisiones particulares de este set:

- Escala común por personaje: las hojas B de cada personaje (ataque, daño, muerte) usan la
  escala medida en su hoja A, así el personaje no cambia de tamaño al pasar de caminar a morir.
- Idle por respiración: igual que con Ventura, se parte de un único frame y se desplaza el
  torso, para que el enemigo quieto no "hierva" con las micro-diferencias entre imágenes.
- Tono del jefe: en algunas hojas el pelaje del lobo quedó un escalón más claro.
  Se corrige bajando un escalón la rampa de grises en esos frames (nunca en los de Ambrosio
  humano), así el jefe no cambia de color al cambiar de ataque.
- Proyectiles (la máscara del Actor) se recortan a su contenido y se centran en un lienzo chico:
  en el juego son un objeto aparte, con su propio origen en el centro.

Uso: python enemigos.py <carpeta_hojas> <carpeta_assets_pixel>
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from paleta import NOMBRES, PALETA_RGB
from ventura import buscar_hoja, respiracion

AQUI = Path(__file__).parent

GRISES = "tinta levita gris_oscuro gris_medio gris gris_claro blanco".split()
PLATA = "plata_oscura plata luna".split()
PIEL = "piel piel_sombra".split()
MORADO = "morado_oscuro morado morado_claro".split()

# Cada personaje: lienzo, fila de los pies, colores permitidos, hojas (con sus opciones de
# pixelizar.py) y animaciones como (hoja, índices de frame). "ESCALA:x" toma la escala de la
# hoja x del mismo personaje.
PERSONAJES = {
    "repintado": {
        "lienzo": (64, 64), "base": 62,
        "colores": ["tinta"] + GRISES[2:] + PIEL + ["bronce", "ambar"] + PLATA[:2],
        "hojas": {
            "a": ("repintado_a", ["--columnas", "4", "--filas", "3", "--referencia", "0", "--alto", "44"]),
            "b": ("repintado_b", ["--columnas", "4", "--filas", "3", "--referencia", "0", "ESCALA:a"]),
        },
        "animaciones": {
            "Idle": ("a", [0, 1, 2]), "Caminar": ("a", [3, 4, 5, 6, 7, 8]),
            "Preparar": ("a", [9, 10]), "Atacar": ("b", [0, 1, 2]),
            "Golpeado": ("b", [3, 4]), "Morir": ("b", [5, 6, 7, 8, 9, 10]),
        },
    },
    "actor": {
        "lienzo": (96, 64), "base": 62, "colores": GRISES + PLATA,
        "hojas": {
            # El Actor viene en una disposición libre (no respeta la grilla), por eso se separa
            # por manchas; "union 3" evita que la máscara en la mano se pegue a otra pose.
            "a": ("actor_a", ["--union", "3", "--referencia", "0", "--alto", "52"]),
            "b": ("actor_b", ["--union", "3", "ESCALA:a"]),
            # La máscara vino dibujada al tamaño de la cara del Actor; como proyectil tiene que
            # leerse como un objeto chico (unos 14 px), así que se reduce con escala propia.
            "p": ("actor_b", ["--union", "3", "--escala", "9.0", "--usar", "7", "8", "12", "13", "14"]),
        },
        "respira": ("a", 0, [0, 0, 1, 1, 1, 0]),
        "animaciones": {
            "Caminar": ("a", [2, 3, 4, 5, 6, 7]), "Preparar": ("a", [8]),
            "Lanzar": ("a", [9]), "Recuperar": ("b", [3]),
            "Golpeado": ("b", [9, 5]), "Morir": ("b", [10, 11, 6]),
        },
        "proyectiles": {"Mascara": ("p", [0, 1, 2, 3], 16), "MascaraRota": ("p", [4], 16)},
    },
    "cuervo": {
        "lienzo": (48, 48), "base": None, "colores": GRISES[:5] + PLATA + ["blanco"],
        "hojas": {
            "a": ("cuervo", ["--columnas", "4", "--filas", "3", "--referencia", "0", "--alto", "22",
                             "--usar", *map(str, range(12)), "--ancla-v", "centro",
                             "--ancla-h", "caja"]),
        },
        "animaciones": {
            "Volar": ("a", [0, 1, 2, 3, 4, 5]), "Picada": ("a", [6, 7, 8]),
            "Golpeado": ("a", [9]), "Morir": ("a", [10, 11]),
        },
    },
    "agente": {
        "lienzo": (112, 72), "base": 70,
        "colores": GRISES + PIEL + ["bronce", "ambar", "llama"] + PLATA,
        "hojas": {
            "a": ("agente_a", ["--columnas", "4", "--filas", "3", "--valles", "--referencia", "0",
                               "--alto", "56"]),
            "b": ("agente_b", ["--columnas", "4", "--filas", "3", "--valles", "--referencia", "0",
                               "ESCALA:a"]),
            # Tirado en el piso es más ancho que de pie: se centra por la caja para no cortarlo.
            "m": ("agente_b", ["--columnas", "4", "--filas", "3", "--valles", "ESCALA:a",
                               "--usar", "6", "7", "8", "9", "10", "11", "--ancla-h", "caja"]),
        },
        "respira": ("a", 0, [0, 0, 1, 1, 1, 0]),
        # Restos del borde de celda de la hoja (línea negra con antialias sobre el verde) que
        # se cuantizan como ámbar justo debajo de las botas.
        "limpiar_pies": (["ambar", "llama"], 2),
        "animaciones": {
            "Caminar": ("a", [3, 4, 5, 6, 7, 8]), "Preparar": ("a", [9, 10]),
            "Golpe": ("b", [2]), "Golpeado": ("b", [3, 4]), "Morir": ("m", [0, 1, 2, 3, 4, 5]),
        },
    },
    "lobo": {
        "lienzo": (192, 128), "base": 126,
        "colores": GRISES + PLATA + MORADO + ["bronce", "crema_sombra"] + PIEL,
        "hojas": {
            # Las poses del jefe se tocan entre celdas (cola con garra): corte por valles.
            "a": ("lobo_a_hoja", ["--columnas", "4", "--filas", "2", "--valles", "--referencia", "0", "--alto", "92"]),
            "b": ("lobo_b", ["--columnas", "4", "--filas", "2", "--valles", "--referencia", "0", "--alto", "92"]),
            "c": ("lobo_c", ["--columnas", "4", "--filas", "2", "--valles", "--referencia", "0", "--alto", "92"]),
            "d": ("lobo_d", ["--columnas", "4", "--filas", "2", "--valles", "--referencia", "0", "--alto", "92",
                             "--usar", "1", "2", "3"]),
            # En la hoja D la fila de abajo quedó dibujada más grande que la de arriba: se mide
            # su escala con su propia pose de pie (el primer lobo de esa fila).
            "d2": ("lobo_d", ["--columnas", "4", "--filas", "2", "--valles", "--referencia", "4", "--alto", "92",
                              "--usar", "4", "5", "6", "7"]),
            "e": ("lobo_e", ["--columnas", "4", "--filas", "2", "--valles", "--referencia", "0", "--alto", "92"]),
        },
        "respira": ("a", 0, [0, 1, 1, 2, 2, 1]),
        "animaciones": {
            "Acechar": ("a", [3, 4, 5, 6]),
            "PrepararEmbestida": ("b", [0, 1]), "Embestida": ("b", [2, 4]),
            "Atascado": ("b", [5]), "Liberarse": ("b", [6]),
            "Zarpazo": ("c", [0, 1, 2]), "Aullido": ("c", [4, 5, 6]),
            "GarraLuna": ("d", [0, 1, 2]), "Transicion": ("d2", [0, 1, 2, 1, 3]),
            "Golpeado": ("e", [0, 1]), "Derrota": ("e", [2, 3, 4, 5, 6]),
        },
        # Frames de lobo (no de Ambrosio humano) que pueden necesitar oscurecer el pelaje.
        "pelaje": {"a": "todos", "b": "todos", "c": "todos", "d": "todos", "d2": [0, 1, 2, 3],
                   "e": [0, 1, 2, 3, 4]},
    },
    "ambrosio": {
        "lienzo": (96, 64), "base": 62,
        "colores": GRISES + PIEL + ["bronce", "ambar", "llama", "crema_sombra"],
        "hojas": {
            "a": ("farolero", ["--union", "3", "--referencia", "0", "--alto", "46",
                               "--usar", "0", "1", "2"]),
        },
        "respira": ("a", 0, [0, 0, 1, 1, 1, 0]),
        "animaciones": {"Caminar": ("a", [1]), "Farol": ("a", [2])},
    },
}

PALETA = np.array(PALETA_RGB)
RAMPA = ["levita", "gris_oscuro", "gris_medio", "gris", "gris_claro"]


def pixelizar(hoja, opciones, destino, lienzo, base, colores):
    cmd = [sys.executable, str(AQUI / "pixelizar.py"), str(hoja), str(destino), "--nombre", "f",
           "--lienzo", str(lienzo[0]), str(lienzo[1]), "--colores", *colores,
           "--contorno-selectivo", *opciones]
    if base is not None:
        cmd += ["--base", str(base)]
    salida = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    informe = json.loads(salida.strip().splitlines()[-1])
    frames = [np.asarray(Image.open(Path(destino) / f"f_{i + 1}.png").convert("RGBA"))
              for i in range(len(informe["frames"]))]
    return frames, informe


def indices_paleta(frame):
    rgb = frame[..., :3].reshape(-1, 1, 3).astype(np.int32)
    return ((rgb - PALETA[None]) ** 2).sum(-1).argmin(-1).reshape(frame.shape[:2])


def oscurecer_pelaje(frame):
    """Si el gris oscuro domina sobre el casi-negro, la pose quedó un escalón más clara."""
    idx = indices_paleta(frame)
    opaco = frame[..., 3] > 0
    cuenta = {n: int((opaco & (idx == NOMBRES.index(n))).sum()) for n in RAMPA}
    if cuenta["gris_oscuro"] <= cuenta["levita"]:
        return frame
    nuevo = frame.copy()
    for claro, oscuro in zip(RAMPA[1:], RAMPA[:-1]):
        nuevo[opaco & (idx == NOMBRES.index(claro)), :3] = PALETA[NOMBRES.index(oscuro)]
    return nuevo


def limpiar_pies(frame, colores, filas):
    ys = np.nonzero(frame[..., 3] > 0)[0]
    if not len(ys):
        return frame
    idx = indices_paleta(frame)
    nuevo = frame.copy()
    zona = np.zeros(frame.shape[:2], bool)
    zona[ys.max() - filas + 1:] = True
    for c in colores:
        nuevo[zona & (idx == NOMBRES.index(c))] = 0
    return nuevo


def centrar(frame, tam):
    ys, xs = np.nonzero(frame[..., 3] > 0)
    fig = frame[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    lienzo = np.zeros((tam, tam, 4), np.uint8)
    h, w = min(fig.shape[0], tam), min(fig.shape[1], tam)
    y0, x0 = (tam - h) // 2, (tam - w) // 2
    lienzo[y0:y0 + h, x0:x0 + w] = fig[:h, :w]
    return lienzo


def armar(nombre, conf, hojas, salida, tmp):
    convertidas, escalas = {}, {}
    for clave, (archivo, opciones) in conf["hojas"].items():
        opciones = list(opciones)
        for i, o in enumerate(opciones):
            if o.startswith("ESCALA:"):
                opciones[i:i + 1] = ["--escala", f"{escalas[o.split(':')[1]]:.4f}"]
        frames, informe = pixelizar(buscar_hoja(hojas, archivo), opciones,
                                    Path(tmp) / nombre / clave, conf["lienzo"], conf["base"],
                                    conf["colores"])
        pelaje = conf.get("pelaje", {}).get(clave)
        if pelaje:
            elegidos = range(len(frames)) if pelaje == "todos" else pelaje
            frames = [oscurecer_pelaje(f) if i in elegidos else f for i, f in enumerate(frames)]
        if "limpiar_pies" in conf:
            frames = [limpiar_pies(f, *conf["limpiar_pies"]) for f in frames]
        convertidas[clave], escalas[clave] = frames, informe["escala"]

    animaciones = {}
    if "respira" in conf:
        clave, i, pasos = conf["respira"]
        animaciones["Idle"] = respiracion(convertidas[clave][i], pasos)
    for anim, (clave, idx) in conf["animaciones"].items():
        if max(idx) >= len(convertidas[clave]):
            sys.exit(f"{nombre}.{anim}: la hoja '{clave}' dio {len(convertidas[clave])} frames")
        animaciones[anim] = [convertidas[clave][i] for i in idx]
    for anim, (clave, idx, tam) in conf.get("proyectiles", {}).items():
        animaciones[anim] = [centrar(convertidas[clave][i], tam) for i in idx]

    destino = salida / nombre
    destino.mkdir(parents=True, exist_ok=True)
    for vieja in destino.glob("*.png"):
        vieja.unlink()
    for anim, frames in animaciones.items():
        for i, f in enumerate(frames):
            Image.fromarray(f).save(destino / f"{anim}_{i + 1}.png")
    return {a: len(f) for a, f in animaciones.items()}, {k: round(v, 3) for k, v in escalas.items()}


def main():
    hojas, salida = Path(sys.argv[1]), Path(sys.argv[2])
    elegidos = sys.argv[3:] or list(PERSONAJES)
    with tempfile.TemporaryDirectory() as tmp:
        for nombre in elegidos:
            anims, escalas = armar(nombre, PERSONAJES[nombre], hojas, salida, tmp)
            print(nombre, json.dumps(anims, ensure_ascii=False), "escalas", escalas)


if __name__ == "__main__":
    main()
