"""Botones de los controles táctiles y el destello blanco de pantalla.

Los botones se dibujan con la misma paleta cerrada del juego (tinta, levita y el morado de
Ventura) para que no parezcan un control genérico pegado encima. Son de 40 px: escalados a la
pantalla de un celular quedan por encima del mínimo cómodo para un pulgar, y el ícono es de
trazo grueso porque se mira de reojo mientras se juega.

Uso: python tactil.py <carpeta_hud>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

from paleta import PALETA_HEX, hex_a_rgb

T = 40
TINTA = hex_a_rgb(PALETA_HEX["tinta"]) + (255,)
LEVITA = hex_a_rgb(PALETA_HEX["levita"]) + (215,)
BORDE = hex_a_rgb(PALETA_HEX["morado_claro"]) + (255,)
ICONO = hex_a_rgb(PALETA_HEX["luna"]) + (255,)
AMBAR = hex_a_rgb(PALETA_HEX["llama"]) + (255,)


def base():
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((1, 1, T - 2, T - 2), fill=TINTA)
    d.ellipse((3, 3, T - 4, T - 4), fill=LEVITA, outline=BORDE, width=2)
    return im, d


def flecha(d, izquierda):
    if izquierda:
        d.polygon([(12, 20), (24, 10), (24, 30)], fill=ICONO)
    else:
        d.polygon([(28, 20), (16, 10), (16, 30)], fill=ICONO)


def saltar(d):
    d.polygon([(20, 9), (31, 21), (24, 21), (24, 30), (16, 30), (16, 21), (9, 21)], fill=ICONO)


def carta(d):
    d.rectangle((13, 10, 27, 30), fill=ICONO)
    d.rectangle((15, 12, 25, 28), outline=TINTA, width=1)
    d.ellipse((17, 16, 23, 22), fill=hex_a_rgb(PALETA_HEX["morado"]) + (255,))


def farol(d):
    d.rectangle((17, 8, 23, 10), fill=ICONO)
    d.rectangle((14, 11, 26, 29), outline=ICONO, width=2)
    d.ellipse((17, 15, 23, 25), fill=AMBAR)
    d.rectangle((15, 30, 25, 31), fill=ICONO)


def parry(d):
    d.polygon([(20, 8), (30, 12), (28, 24), (20, 31), (12, 24), (10, 12)], fill=ICONO)
    d.polygon([(20, 12), (26, 14), (25, 23), (20, 27)], fill=hex_a_rgb(PALETA_HEX["morado"]) + (255,))


def pausa(d):
    d.rectangle((14, 12, 18, 28), fill=ICONO)
    d.rectangle((22, 12, 26, 28), fill=ICONO)


BOTONES = {"Izq": lambda d: flecha(d, True), "Der": lambda d: flecha(d, False), "Saltar": saltar,
           "Carta": carta, "Farol": farol, "Parry": parry, "Pausa": pausa}


def main(destino):
    carpeta = Path(destino) / "tactil"
    carpeta.mkdir(parents=True, exist_ok=True)
    for nombre, dibujar in BOTONES.items():
        im, d = base()
        dibujar(d)
        im.save(carpeta / f"Boton{nombre}_1.png")
    Image.new("RGBA", (4, 4), (255, 255, 255, 255)).save(Path(destino) / "Blanco.png")
    print("botones táctiles:", ", ".join(BOTONES), "->", carpeta)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
