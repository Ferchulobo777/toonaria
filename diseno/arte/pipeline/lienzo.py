"""Herramientas mínimas para dibujar pixel art por código con la paleta cerrada del juego.

Todo se dibuja con colores de `paleta.py` (por nombre), así ningún asset procedural puede
salirse de la paleta. Las coordenadas son en píxeles reales del juego (sin escalar).
"""

from pathlib import Path

import numpy as np
from PIL import Image

from paleta import PALETA_HEX, hex_a_rgb

COLOR = {nombre: (*hex_a_rgb(h), 255) for nombre, h in PALETA_HEX.items()}


class Lienzo:
    def __init__(self, ancho, alto):
        self.w, self.h = ancho, alto
        self.a = np.zeros((alto, ancho, 4), dtype=np.uint8)

    @staticmethod
    def _c(color):
        return COLOR[color] if isinstance(color, str) else color

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[int(y), int(x)] = self._c(color)

    def rect(self, x0, y0, x1, y1, color):
        """Rectángulo relleno, coordenadas inclusivas."""
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, self.w - 1), min(y1, self.h - 1)
        if x0 <= x1 and y0 <= y1:
            self.a[y0:y1 + 1, x0:x1 + 1] = self._c(color)

    def hline(self, x0, x1, y, color):
        self.rect(x0, y, x1, y, color)

    def vline(self, x, y0, y1, color):
        self.rect(x, y0, x, y1, color)

    def linea(self, x0, y0, x1, y1, color):
        """Línea de Bresenham (sin antialiasing)."""
        x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def elipse(self, cx, cy, rx, ry, color, relleno=True):
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        d = ((xs - cx) / max(rx, 0.5)) ** 2 + ((ys - cy) / max(ry, 0.5)) ** 2
        if relleno:
            m = d <= 1.0
        else:
            m = (d <= 1.0) & (d >= (1 - 1.6 / max(min(rx, ry), 1)) ** 2)
        self.a[m] = self._c(color)

    def mascara(self):
        return self.a[..., 3] > 0

    def contorno(self, color="tinta", diagonales=False):
        """Agrega un contorno exterior de 1 px alrededor de todo lo dibujado."""
        m = self.mascara()
        p = np.pad(m, 1)
        vec = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
        if diagonales:
            vec |= p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:]
        self.a[vec & ~m] = self._c(color)

    def reemplazar(self, desde, hacia):
        c = np.array(self._c(desde))
        m = np.all(self.a == c, axis=-1)
        self.a[m] = self._c(hacia)

    def pegar(self, otro, x, y):
        """Pega otro lienzo (o arreglo RGBA) respetando la transparencia."""
        src = otro.a if isinstance(otro, Lienzo) else otro
        h, w = src.shape[:2]
        for j in range(h):
            for i in range(w):
                if src[j, i, 3] and 0 <= x + i < self.w and 0 <= y + j < self.h:
                    self.a[y + j, x + i] = src[j, i]

    def copia(self):
        n = Lienzo(self.w, self.h)
        n.a = self.a.copy()
        return n

    def imagen(self):
        return Image.fromarray(self.a)

    def guardar(self, ruta):
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        self.imagen().save(ruta)
        return ruta


def tramado(lienzo, x0, y0, x1, y1, color, patron="damero"):
    """Trama (dithering) ordenada: la forma clásica de hacer degradés en pixel art."""
    for y in range(max(y0, 0), min(y1 + 1, lienzo.h)):
        for x in range(max(x0, 0), min(x1 + 1, lienzo.w)):
            if patron == "damero" and (x + y) % 2 == 0:
                lienzo.px(x, y, color)
            elif patron == "ralo" and x % 2 == 0 and y % 2 == 0:
                lienzo.px(x, y, color)
            elif patron == "muy_ralo" and x % 4 == 0 and y % 4 == (x // 4) % 2 * 2:
                lienzo.px(x, y, color)
