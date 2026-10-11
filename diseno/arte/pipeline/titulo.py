"""Assets de la pantalla de título, a partir del arte del proyecto.

- Fondo: la ilustración del Corazón de Toonaria (torre del reloj recortada contra la luna),
  ya pixelizada para el nivel 3. Se encuadra la luna arriba, detrás del logo, como halo, y la
  parte baja se oscurece con trama para que el menú se lea.
- Logo: el logo aprobado (logo_toonaria.png) reducido a ~300 px con paleta propia de 18 colores
  y contorno de tinta preservado.

Uso: python titulo.py <carpeta_assets_pixel> <logo.png>
"""

import sys
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from PIL import Image

from fondos_ilustrados import BAYER4, kmeans
from pixelizar import rgb_a_lab


def fondo(px):
    f = px / "fondos"
    cielo = Image.open(f / "n3_cielo.png").convert("RGBA")
    ciudad = Image.open(f / "n3_ciudad.png").convert("RGBA")
    cielo.alpha_composite(ciudad)
    img = np.asarray(cielo.crop((0, 20, 640, 380))).astype(np.float64)
    h, w = img.shape[:2]
    tinta = np.array([18, 16, 20, 255])
    for y in range(h):
        t = max(0.0, (y - 190) / (h - 190))  # oscurecer desde el tercio inferior
        umbral = BAYER4[y % 4, np.arange(w) % 4]
        oscuro = umbral < t * 0.6
        img[y][oscuro] = tinta
    Image.fromarray(img.astype(np.uint8)).save(px / "titulo" / "fondo.png")


def logo(px, ruta, ancho=340):
    im = Image.open(ruta).convert("RGBA")
    # Sólo la palabra TOONARIA: la luna y la torre del logo ya están en el fondo del título.
    # Cada letra tiene un trazo claro alrededor; rellenando ese trazo queda la silueta exacta
    # de las letras, sin la franja de edificios que el logo tiene detrás de la palabra.
    a = np.asarray(im).astype(np.float64)
    lum, sat = a[..., :3].mean(-1), a[..., :3].max(-1) - a[..., :3].min(-1)
    trazo = (lum > 140) & (sat < 40) & (a[..., 3] > 128)
    lleno = ndi.binary_fill_holes(trazo)
    etiquetas, n = ndi.label(lleno)
    centros = ndi.center_of_mass(lleno, etiquetas, range(1, n + 1))
    areas = ndi.sum(lleno, etiquetas, range(1, n + 1))
    alto_img = a.shape[0]
    letras = [k + 1 for k in range(n) if centros[k][0] > 0.42 * alto_img and areas[k] > 1500]
    mascara = ndi.binary_dilation(np.isin(etiquetas, letras), iterations=4)
    a[..., 3] = np.where(mascara, a[..., 3], 0)
    im = Image.fromarray(a.astype(np.uint8))
    caja = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    im = im.crop(caja)
    alto = round(im.height * ancho / im.width)
    grande = np.asarray(im.resize((ancho * 2, alto * 2), Image.LANCZOS)).astype(np.float64)
    chico = np.asarray(im.resize((ancho, alto), Image.BOX)).astype(np.float64)
    opaco = chico[..., 3] > 110
    rgb = chico[..., :3]
    paleta = kmeans(rgb[opaco][::2], 18, semilla=5)
    paleta = np.vstack([paleta, [[18, 16, 20]]])
    pl = rgb_a_lab(paleta)
    lab = rgb_a_lab(rgb.reshape(-1, 3)).reshape(alto, ancho, 3)
    idx = ((lab[:, :, None, :] - pl[None, None]) ** 2).sum(-1).argmin(-1)
    lum = grande[..., :3].mean(-1)
    oscuro = ((lum < 60) & (grande[..., 3] > 128)).astype(float)
    lineas = oscuro.reshape(alto, 2, ancho, 2).mean((1, 3))
    idx = np.where(lineas >= 0.3, len(paleta) - 1, idx)
    salida = np.zeros((alto, ancho, 4), np.uint8)
    salida[..., :3] = np.clip(np.round(paleta[idx]), 0, 255)
    salida[..., 3] = np.where(opaco, 255, 0)
    # Contorno exterior de tinta de 1 px: el logo se recorta sobre el cielo claro de la luna.
    m = opaco
    p = np.pad(m, 1)
    borde = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~m
    salida[borde] = (18, 16, 20, 255)
    Image.fromarray(salida).save(px / "titulo" / "logo.png")
    print("logo", ancho, "x", alto)


if __name__ == "__main__":
    px = Path(sys.argv[1])
    (px / "titulo").mkdir(parents=True, exist_ok=True)
    fondo(px)
    logo(px, sys.argv[2])
