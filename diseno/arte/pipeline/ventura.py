"""Arma el set completo de animaciones de Ventura a partir de sus hojas de animación.

Cada hoja se pixeliza con `pixelizar.py` y después se eligen y ordenan los frames que
componen cada animación del juego. Dos animaciones se construyen a mano sobre el pixel art ya
convertido, porque dibujadas pose por pose no dan buen resultado:

- Idle: si cada frame sale de una imagen distinta, aparecen micro-diferencias que hacen
  "hervir" al personaje cuando está quieto. Se parte de un único frame y se anima la
  respiración desplazando el torso un píxel, como se hace en el pixel art tradicional.
- Doble salto: la vuelta en el aire se arma rotando la pose agrupada en pasos de 90 grados,
  que es una rotación exacta en una grilla de píxeles (no deforma ni agrega colores).

Uso: python ventura.py <carpeta_hojas> <carpeta_salida>
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).parent
LIENZO = (96, 64)
BASE = 62
ALTO = 48
COLORES = ("tinta levita gris_oscuro gris_medio gris_claro blanco piel piel_sombra crema "
           "crema_sombra morado_oscuro morado morado_claro luna bronce ambar llama").split()

# hoja -> opciones de pixelizar.py
HOJAS = {
    "idle": ["--columnas", "4", "--filas", "2"],
    "correr": ["--columnas", "4", "--filas", "2"],
    "salto_pies": ["--referencia", "0", "--union", "3"],
    "salto_aire": ["--referencia", "0", "--union", "3", "--ancla-v", "cabeza"],
    "doble": ["--referencia", "0", "--columnas", "4", "--filas", "2", "--ancla-v", "centro"],
    "carga": ["--referencia", "0", "--columnas", "4", "--filas", "2"],
    "arrojar": ["--referencia", "0", "--union", "3", "--borrar", "240", "520", "392", "768"],
    "dano": ["--referencia", "0", "--union", "3"],
    "parry": ["--referencia", "0"],
}
ARCHIVO = {"salto_pies": "salto", "salto_aire": "salto"}

# animación del juego -> (hoja, frames en orden; índices sin contar la pose de referencia)
ANIMACIONES = {
    "Correr": ("correr", [0, 1, 2, 3, 4, 5, 6, 7]),
    "SaltoInicio": ("salto_pies", [0]),
    "Subida": ("salto_aire", [1, 2]),
    "Apice": ("salto_aire", [3, 4]),
    "Caida": ("salto_aire", [5, 6]),
    "Aterrizaje": ("salto_pies", [7]),
    "Carga1": ("carga", [0, 1]),
    "Carga2": ("carga", [2, 3]),
    "CargaCompleta": ("carga", [4, 5, 6]),
    "Arrojar": ("arrojar", [1, 2, 3]),
    "LanzarFarol": ("arrojar", [4, 5, 6]),
    "RecibirDano": ("dano", [0, 1]),
    "Recuperacion": ("dano", [2]),
    "Derrota": ("dano", [3, 4, 5, 6]),
    "Parry": ("parry", [0, 1, 2, 3]),
    "Victoria": ("parry", [4, 5, 6]),
}


def buscar_hoja(carpeta, nombre):
    """Las hojas se guardan en WebP sin pérdida (pesan un tercio que el PNG original)."""
    for ext in (".webp", ".png"):
        if (carpeta / f"{nombre}{ext}").exists():
            return carpeta / f"{nombre}{ext}"
    sys.exit(f"no se encontró la hoja {nombre} en {carpeta}")


def pixelizar(hoja, opciones, destino):
    cmd = [sys.executable, str(AQUI / "pixelizar.py"), str(hoja), str(destino),
           "--nombre", "f", "--alto", str(ALTO), "--lienzo", str(LIENZO[0]), str(LIENZO[1]),
           "--base", str(BASE), "--colores", *COLORES, "--contorno-selectivo", *opciones]
    salida = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    informe = json.loads(salida.strip().splitlines()[-1])
    frames = [np.asarray(Image.open(Path(destino) / f"f_{i + 1}.png").convert("RGBA"))
              for i in range(len(informe["frames"]))]
    return frames, informe


def respiracion(frame, desplazamientos):
    """Baja la parte superior del cuerpo (por encima de la cadera) n píxeles por frame."""
    opacas = np.nonzero(frame[..., 3] > 0)[0]
    arriba, abajo = opacas.min(), opacas.max()
    cadera = arriba + int((abajo - arriba) * 0.62)
    resultado = []
    for d in desplazamientos:
        f = frame.copy()
        if d:
            parte = frame[:cadera].copy()
            f[:cadera] = 0
            f[d:cadera + d] = np.where(parte[..., 3:4] > 0, parte, f[d:cadera + d])
            # La línea de la cadera queda cubierta por el torso desplazado; lo que estaba
            # debajo sigue siendo la pierna original, así que no se abre ningún hueco.
        resultado.append(f)
    return resultado


def vuelta(frame):
    """Cuatro cuartos de giro alrededor del centro de la figura (sentido horario)."""
    alto, ancho = frame.shape[:2]
    ys, xs = np.nonzero(frame[..., 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    figura = frame[y0:y1, x0:x1]
    cy, cx = (y0 + y1) / 2, (x0 + x1) / 2
    resultado = []
    for k in range(4):
        rot = np.rot90(figura, -k)
        lienzo = np.zeros_like(frame)
        h, w = rot.shape[:2]
        ty, tx = int(round(cy - h / 2)), int(round(cx - w / 2))
        lienzo[max(ty, 0):ty + h, max(tx, 0):tx + w] = rot[max(-ty, 0):, max(-tx, 0):][
            :alto - max(ty, 0), :ancho - max(tx, 0)]
        resultado.append(lienzo)
    return resultado


def main():
    hojas, salida = Path(sys.argv[1]), Path(sys.argv[2])
    salida.mkdir(parents=True, exist_ok=True)
    convertidas, informes = {}, {}
    with tempfile.TemporaryDirectory() as tmp:
        for nombre, opciones in HOJAS.items():
            archivo = buscar_hoja(hojas, f"ventura_{ARCHIVO.get(nombre, nombre)}")
            convertidas[nombre], informes[nombre] = pixelizar(
                archivo, opciones, Path(tmp) / nombre)

    for nombre, (h, idx) in ANIMACIONES.items():
        if max(idx) >= len(convertidas[h]):
            sys.exit(f"{nombre}: la hoja '{h}' dio {len(convertidas[h])} frames "
                     f"(alturas {informes[h]['alturas_fuente']})")
    animaciones = {nombre: [convertidas[h][i] for i in idx]
                   for nombre, (h, idx) in ANIMACIONES.items()}
    animaciones["Idle"] = respiracion(convertidas["idle"][0], [0, 0, 1, 1, 1, 0])
    giro = vuelta(convertidas["doble"][0])
    animaciones["SaltoDoble"] = giro + [convertidas["doble"][6]]

    for nombre, frames in animaciones.items():
        for i, f in enumerate(frames):
            Image.fromarray(f).save(salida / f"{nombre}_{i + 1}.png")
    print(json.dumps({n: len(f) for n, f in animaciones.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
