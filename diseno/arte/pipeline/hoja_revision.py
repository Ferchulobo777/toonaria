"""Arma una hoja de revisión con todas las animaciones de un personaje (una fila cada una).

Sirve para controlar consistencia de tamaño, paleta y alineación entre animaciones antes de
importarlas al motor. No forma parte del juego.

Uso: python hoja_revision.py <carpeta_frames> <salida.png> [zoom]
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    carpeta, destino = Path(sys.argv[1]), Path(sys.argv[2])
    zoom = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    grupos = defaultdict(list)
    for f in carpeta.glob("*.png"):
        m = re.match(r"(.+)_(\d+)\.png$", f.name)
        if m:
            grupos[m.group(1)].append((int(m.group(2)), f))
    nombres = sorted(grupos)
    ejemplo = Image.open(next(iter(grupos.values()))[0][1])
    w, h = ejemplo.size[0] * zoom, ejemplo.size[1] * zoom
    margen = 150
    columnas = max(len(v) for v in grupos.values())
    hoja = Image.new("RGBA", (margen + columnas * w, len(nombres) * h), (74, 70, 82, 255))
    dibujo = ImageDraw.Draw(hoja)
    for fila, nombre in enumerate(nombres):
        y = fila * h
        if fila % 2:
            dibujo.rectangle([0, y, hoja.width, y + h], fill=(84, 80, 92, 255))
        dibujo.text((8, y + h // 2 - 6), f"{nombre} ({len(grupos[nombre])})", fill=(235, 230, 240))
        # Línea de piso de referencia (fila de los pies en el lienzo).
        piso = y + (ejemplo.size[1] - 2) * zoom + zoom
        dibujo.line([margen, piso, hoja.width, piso], fill=(120, 110, 135), width=1)
        for col, (_, f) in enumerate(sorted(grupos[nombre])):
            img = Image.open(f).convert("RGBA").resize((w, h), Image.NEAREST)
            hoja.alpha_composite(img, (margen + col * w, y))
    hoja.save(destino)
    print(destino, hoja.size)


if __name__ == "__main__":
    main()
