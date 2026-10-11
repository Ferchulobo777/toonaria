"""Convierte las ilustraciones de cada barrio en fondos pixel art con capas de parallax.

Los fondos del juego salen de las ilustraciones aprobadas del proyecto
(diseno/arte/escenarios/nivel*.jpg),
no de arte nuevo: se encadenan los tramos de cada barrio en una tira continua, se pixelizan y se
separan en capas de profundidad para que el parallax tenga volumen.

Pasos:
1. Cada tramo se escala al alto de pantalla. Las líneas de tinta se miden en cada tramo por
   separado (a doble resolución) para no perderlas al reducir.
2. Los tramos se encadenan pasando por niebla: a lo largo de la unión la imagen se funde con
   una versión muy desenfocada de ambos lados, con trama. Las ilustraciones no fueron dibujadas
   para empalmar exacto, y la niebla es parte del mundo, así que el corte se lee como cruzar
   un banco de bruma entre una calle y la otra.
3. Separación del cielo sobre la imagen suave: es lo que se alcanza desde el borde superior
   sin cruzar una línea de tinta. Detrás de los edificios el cielo se completa estirando su
   color hacia abajo, así puede moverse más lento que la ciudad sin dejar huecos.
4. Ajuste por capa: la ciudad baja un poco de brillo y el cielo se acerca al color de la niebla.
   Es el mismo criterio de los plataformeros 2D: el fondo un escalón por detrás de los
   personajes para que la acción se lea primero.
5. Pixelizado con paleta adaptativa del barrio (k-means en Lab) y trama ordenada de Bayer.
6. Tiles de piso del barrio con colores tomados de esa misma paleta, para que el piso jugable
   se lea como la misma calle de la ilustración.

Los interiores (la carpa del prólogo y la cima de la torre) se procesan con --interior: no
hay cielo que separar ni nubes, y el piso de esas escenas se dibuja aparte (tablas y rejilla de
hierro), así que tampoco se generan tiles.

Uso: python fondos_ilustrados.py <nivel> <carpeta_assets_pixel> [--alto=N] [--interior] <img1> [<img2> ...]
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from lienzo import Lienzo
from objetos_juego import adoquines, cornisa, muro_ladrillos
from pixelizar import rgb_a_lab

ALTO = 360
BAYER4 = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16


def cargar_tramo(ruta, alto):
    im = Image.open(ruta).convert("RGB")
    w = round(im.width * alto / im.height)
    grande = np.asarray(im.resize((w * 2, alto * 2), Image.LANCZOS)).astype(np.float64)
    chico = np.asarray(im.resize((w, alto), Image.BOX)).astype(np.float64)
    lum = grande.mean(-1)
    oscuro = (lum < np.percentile(lum, 9)).astype(np.float64)
    lineas = oscuro.reshape(alto, 2, w, 2).mean((1, 3))
    return chico, lineas


def encadenar(tramos, ancho_union=180):
    chico, lineas = tramos[0]
    for sig, sig_lineas in tramos[1:]:
        h = chico.shape[0]
        f = ancho_union
        a, b = chico[:, -f:], sig[:, :f]
        t = (np.arange(f) + 0.5) / f
        cruce = a * (1 - t)[None, :, None] + b * t[None, :, None]
        bruma = ndi.gaussian_filter(cruce, (6, 18, 0))
        bruma = bruma * 0.75 + np.array([205, 196, 178]) * 0.25  # aclara: es niebla
        umbral = BAYER4[np.arange(h)[:, None] % 4, np.arange(f)[None, :] % 4]
        usa_a = (t < 0.5)[None, :] & (umbral >= t[None, :] * 2)
        usa_b = (t >= 0.5)[None, :] & (umbral < (t[None, :] - 0.5) * 2)
        union = np.where(usa_a[..., None], a, np.where(usa_b[..., None], b, bruma))
        union_l = np.where(usa_a, lineas[:, -f:], np.where(usa_b, sig_lineas[:, :f], 0))
        chico = np.concatenate([chico[:, :-f], union, sig[:, f:]], axis=1)
        lineas = np.concatenate([lineas[:, :-f], union_l, sig_lineas[:, f:]], axis=1)
    return chico, lineas


def kmeans(colores, k, iteraciones=14, semilla=0):
    rnd = np.random.default_rng(semilla)
    lab = rgb_a_lab(colores)
    centros = lab[rnd.choice(len(lab), k, replace=False)]
    for _ in range(iteraciones):
        asign = ((lab[:, None, :] - centros[None]) ** 2).sum(-1).argmin(1)
        for j in range(k):
            m = asign == j
            if m.any():
                centros[j] = lab[m].mean(0)
    return np.array([colores[asign == j].mean(0) if (asign == j).any() else colores[0]
                     for j in range(k)])


def cuantizar(chico, lineas, paleta, fuerza_trama=10.0, umbral_linea=0.28):
    h, w = chico.shape[:2]
    pal_lab = rgb_a_lab(paleta)
    lab = rgb_a_lab(chico.reshape(-1, 3)).reshape(h, w, 3)
    lab[..., 0] += (BAYER4[np.arange(h)[:, None] % 4, np.arange(w)[None, :] % 4] - 0.5) * fuerza_trama
    idx = np.empty((h, w), dtype=np.int64)
    for y0 in range(0, h, 60):  # por franjas, para no armar una matriz gigante en memoria
        d = ((lab[y0:y0 + 60, :, None, :] - pal_lab[None, None]) ** 2).sum(-1)
        idx[y0:y0 + 60] = d.argmin(-1)
    tinta = int(np.argmin(pal_lab[:, 0]))
    return np.where(lineas >= umbral_linea, tinta, idx)


def separar_cielo(chico, limite_y, umbral_borde=7.0):
    """Lo que se alcanza desde el borde superior sin cruzar una línea es cielo.

    Las torres lejanas tapadas por la niebla tienen bordes débiles y quedan del lado del cielo,
    lo cual es correcto: están tan lejos que deben moverse con él.
    """
    h, w = chico.shape[:2]
    L = rgb_a_lab(ndi.gaussian_filter(chico, (0.8, 0.8, 0)).reshape(-1, 3)).reshape(h, w, 3)[..., 0]
    borde = np.hypot(ndi.sobel(L, 0), ndi.sobel(L, 1)) / 4
    oscuro = L < np.percentile(L, 12)
    barrera = ndi.binary_dilation((borde > umbral_borde) | oscuro, iterations=1)
    pasable = ~barrera
    pasable[limite_y:] = False
    etiquetas, _ = ndi.label(pasable)
    arriba = np.unique(etiquetas[0][etiquetas[0] > 0])
    cielo = np.isin(etiquetas, arriba)
    cielo = ndi.binary_closing(cielo, iterations=1)
    return ndi.binary_fill_holes(cielo) & (np.arange(h)[:, None] < limite_y)


def completar_cielo(chico, cielo):
    h, w = cielo.shape
    filas = np.where(cielo, np.arange(h)[:, None], -1)
    ultima = np.maximum.accumulate(filas, axis=0).clip(0)
    estirado = chico[ultima, np.arange(w)[None, :]]
    return np.where(cielo[..., None], chico, ndi.uniform_filter(estirado, (1, 21, 1)))


def a_rgba(idx, paleta, mascara=None):
    rgb = np.clip(np.round(paleta[idx]), 0, 255).astype(np.uint8)
    alfa = np.full(idx.shape + (1,), 255, np.uint8)
    if mascara is not None:
        alfa[~mascara] = 0
    return Image.fromarray(np.concatenate([rgb, alfa], -1))


def tiles_del_barrio(nivel, paleta, destino):
    """Piso jugable con los tonos de la calle de la ilustración (los más oscuros y neutros)."""
    lab = rgb_a_lab(paleta)
    croma = np.hypot(lab[:, 1], lab[:, 2])
    orden = [i for i in np.argsort(lab[:, 0]) if croma[i] < 22]
    def tono(fr):
        return tuple(int(v) for v in np.round(paleta[orden[int(fr * (len(orden) - 1))]])) + (255,)
    tinta = tuple(int(v) for v in np.round(paleta[int(np.argmin(lab[:, 0]))])) + (255,)
    junta, piedra, luz, cordon = tono(0.08), tono(0.3), tono(0.45), tono(0.62)
    muro_ladrillos((tinta, junta, piedra, tinta), 11).guardar(destino / f"{nivel}_suelo.png")
    adoquines((tinta, piedra, luz, cordon), 12).guardar(destino / f"{nivel}_borde.png")
    cornisa((tinta, piedra, cordon, junta)).guardar(destino / f"{nivel}_cornisa.png")


def generar_nubes(nivel, paleta, destino, semilla=3):
    """Nubes y bruma del barrio con su propia paleta, repetibles en horizontal.

    Se dibujan con "envoltura" (x módulo ancho) para que el borde derecho empalme con el
    izquierdo: en el juego son mosaicos (TiledSprite) que se desplazan sin fin con el viento.
    """
    lab = rgb_a_lab(paleta)
    orden = np.argsort(lab[:, 0])
    def col(fr):
        c = paleta[orden[int(fr * (len(orden) - 1))]]
        return tuple(int(v) for v in np.round(c)) + (255,)
    sombra, cuerpo, luz = col(0.62), col(0.78), col(0.93)
    rnd = np.random.default_rng(semilla)
    for nombre, ancho, alto, cantidad, escala in (("nubes_lejos", 640, 90, 7, 0.6),
                                                  ("nubes_cerca", 960, 130, 6, 1.0)):
        c = Lienzo(ancho, alto)
        for _ in range(cantidad):
            cx = rnd.uniform(0, ancho)
            cy = rnd.uniform(alto * 0.35, alto * 0.7)
            largo = rnd.uniform(60, 120) * escala
            for k in range(int(5 + 4 * escala)):
                bx = cx + rnd.uniform(-largo / 2, largo / 2)
                by = cy + rnd.uniform(-6, 4) * escala
                r = rnd.uniform(8, 18) * escala
                for capa, colr, dy, f in ((0, sombra, 2, 1.0), (1, cuerpo, 0, 0.9), (2, luz, -3, 0.55)):
                    for y in range(int(by - r), int(by + r) + 1):
                        for x in range(int(bx - r * 1.6), int(bx + r * 1.6) + 1):
                            if ((x - bx) / 1.6) ** 2 + (y - by - dy) ** 2 <= (r * f) ** 2 and 0 <= y < alto:
                                c.px(x % ancho, y, colr)
            # base plana con trama: las nubes de los dibujos animados viejos tienen panza recta
        for y in range(alto):
            for x in range(ancho):
                if c.a[y, x, 3] and (y + 1 >= alto or not c.a[y + 1, x, 3]) and (x + y) % 2:
                    c.px(x, y, sombra)
        c.guardar(destino / f"{nivel}_{nombre}.png")
    # Bruma de primer plano: franja tramada que pasa delante de la acción, muy rala.
    b = Lienzo(640, 48)
    for y in range(48):
        densidad = 1 - abs(y - 30) / 30
        for x in range(640):
            ruido = (np.sin(x * 0.045) + np.sin(x * 0.11 + 1.3)) * 0.25 + 0.5
            if densidad * ruido > 0.55 and (x + 2 * y) % 4 == 0:
                b.px(x, y, luz)
            elif densidad * ruido > 0.42 and (x + 2 * y) % 8 == 0:
                b.px(x, y, cuerpo)
    b.guardar(destino / f"{nivel}_bruma.png")


def main():
    nivel, assets = sys.argv[1], Path(sys.argv[2])
    rutas = sys.argv[3:]
    global ALTO
    interior = "--interior" in rutas
    rutas = [r for r in rutas if r != "--interior"]
    if rutas and rutas[0].startswith("--alto="):
        ALTO = int(rutas.pop(0).split("=")[1])
    fondos = assets / "fondos"
    fondos.mkdir(parents=True, exist_ok=True)
    chico, lineas = encadenar([cargar_tramo(r, ALTO) for r in rutas])
    if interior:
        cielo = np.zeros(chico.shape[:2], bool)
        paleta = np.vstack([kmeans(chico.reshape(-1, 3)[::7], 30, semilla=len(nivel)), [[18, 16, 20]]])
        a_rgba(cuantizar(chico * 0.9, lineas, paleta), paleta).save(fondos / f"{nivel}_ciudad.png")
        np.save(fondos / f"_{nivel}_paleta.npy", paleta)
        print(nivel, "interior", chico.shape[1], "x", chico.shape[0])
        return
    cielo = separar_cielo(chico, limite_y=int(ALTO * 0.66))
    niebla = np.array([214, 206, 190])
    # El ajuste de tono pasa de "ciudad" a "cielo" en forma gradual alrededor del borde entre
    # capas. Con un corte seco, donde la niebla del dibujo es continua (y el cielo llega al
    # límite inferior de la separación) quedaba una línea horizontal de dos brillos distintos.
    m = ndi.gaussian_filter(cielo.astype(np.float64), 5)[..., None]
    def tono(rgb, peso):
        return rgb * (0.86 * (1 - peso) + 0.8 * peso) + niebla * 0.2 * peso
    cielo_rgb = tono(completar_cielo(chico, cielo), np.maximum(m, 0.5))
    ciudad_rgb = tono(chico, m)
    muestra = np.vstack([cielo_rgb[cielo][::5], ciudad_rgb[~cielo][::9]])
    paleta = np.vstack([kmeans(muestra, 30, semilla=len(nivel)), [[18, 16, 20]]])
    idx_cielo = cuantizar(cielo_rgb, np.where(cielo, lineas, 0), paleta)
    idx_ciudad = cuantizar(ciudad_rgb, lineas, paleta)
    a_rgba(idx_cielo, paleta).save(fondos / f"{nivel}_cielo.png")
    a_rgba(idx_ciudad, paleta, ~cielo).save(fondos / f"{nivel}_ciudad.png")
    tiles_del_barrio(nivel, paleta, assets / "tiles")
    generar_nubes(nivel, paleta, fondos)
    np.save(fondos / f"_{nivel}_paleta.npy", paleta)
    print(nivel, "tira", chico.shape[1], "x", chico.shape[0], "cielo %.0f%%" % (cielo.mean() * 100))


if __name__ == "__main__":
    main()
