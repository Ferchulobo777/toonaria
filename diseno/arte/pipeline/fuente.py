"""Fuente bitmap propia del juego (5x7 con descendentes), exportada en formato BMFont.

Se diseñó una tipografía pixel en lugar de usar una TTF porque a 640x360 una fuente vectorial
se suaviza y pierde la grilla; además así cubre todos los caracteres del castellano (tildes,
eñe, diéresis, signos de apertura) sin depender de licencias de terceros. Cada glifo lleva
"horneada" una sombra de tinta de 1 px abajo a la derecha para leerse sobre cualquier fondo.

Uso: python fuente.py <carpeta_salida>
"""

import sys
from pathlib import Path

from PIL import Image

# Filas de -2 a 8 (11 filas): -2/-1 para tildes de mayúsculas, 0..6 cuerpo, 7..8 descendentes.
G = {}


def glifo(caracteres, filas, desde=0):
    for ch in caracteres:
        G[ch] = (desde, [f for f in filas.strip("\n").split("\n")])


glifo("A", """
.###.
#...#
#...#
#####
#...#
#...#
#...#""")
glifo("B", """
####.
#...#
#...#
####.
#...#
#...#
####.""")
glifo("C", """
.###.
#...#
#....
#....
#....
#...#
.###.""")
glifo("D", """
####.
#...#
#...#
#...#
#...#
#...#
####.""")
glifo("E", """
#####
#....
#....
####.
#....
#....
#####""")
glifo("F", """
#####
#....
#....
####.
#....
#....
#....""")
glifo("G", """
.###.
#...#
#....
#.###
#...#
#...#
.###.""")
glifo("H", """
#...#
#...#
#...#
#####
#...#
#...#
#...#""")
glifo("I", """
###
.#.
.#.
.#.
.#.
.#.
###""")
glifo("J", """
..###
...#.
...#.
...#.
#..#.
#..#.
.##..""")
glifo("K", """
#...#
#..#.
#.#..
##...
#.#..
#..#.
#...#""")
glifo("L", """
#....
#....
#....
#....
#....
#....
#####""")
glifo("M", """
#...#
##.##
#.#.#
#.#.#
#...#
#...#
#...#""")
glifo("N", """
#...#
##..#
#.#.#
#..##
#...#
#...#
#...#""")
glifo("O", """
.###.
#...#
#...#
#...#
#...#
#...#
.###.""")
glifo("P", """
####.
#...#
#...#
####.
#....
#....
#....""")
glifo("Q", """
.###.
#...#
#...#
#...#
#.#.#
#..#.
.##.#""")
glifo("R", """
####.
#...#
#...#
####.
#.#..
#..#.
#...#""")
glifo("S", """
.####
#....
#....
.###.
....#
....#
####.""")
glifo("T", """
#####
..#..
..#..
..#..
..#..
..#..
..#..""")
glifo("U", """
#...#
#...#
#...#
#...#
#...#
#...#
.###.""")
glifo("V", """
#...#
#...#
#...#
#...#
#...#
.#.#.
..#..""")
glifo("W", """
#...#
#...#
#...#
#.#.#
#.#.#
#.#.#
.#.#.""")
glifo("X", """
#...#
#...#
.#.#.
..#..
.#.#.
#...#
#...#""")
glifo("Y", """
#...#
#...#
.#.#.
..#..
..#..
..#..
..#..""")
glifo("Z", """
#####
....#
...#.
..#..
.#...
#....
#####""")

glifo("a", """
.....
.....
.###.
....#
.####
#...#
.####""")
glifo("b", """
#....
#....
####.
#...#
#...#
#...#
####.""")
glifo("c", """
....
....
.###
#...
#...
#...
.###""")
glifo("d", """
....#
....#
.####
#...#
#...#
#...#
.####""")
glifo("e", """
.....
.....
.###.
#...#
#####
#....
.###.""")
glifo("f", """
..##
.#..
.#..
####
.#..
.#..
.#..""")
glifo("g", """
.....
.....
.####
#...#
#...#
.####
....#
....#
.###.""")
glifo("h", """
#....
#....
####.
#...#
#...#
#...#
#...#""")
glifo("i", """
#
.
#
#
#
#
#""")
glifo("j", """
..#
...
..#
..#
..#
..#
..#
#.#
.#.""")
glifo("k", """
#...
#...
#..#
#.#.
##..
#.#.
#..#""")
glifo("l", """
#.
#.
#.
#.
#.
#.
.#""")
glifo("m", """
.....
.....
##.#.
#.#.#
#.#.#
#.#.#
#.#.#""")
glifo("n", """
.....
.....
####.
#...#
#...#
#...#
#...#""")
glifo("o", """
.....
.....
.###.
#...#
#...#
#...#
.###.""")
glifo("p", """
.....
.....
####.
#...#
#...#
####.
#....
#....
#....""")
glifo("q", """
.....
.....
.####
#...#
#...#
.####
....#
....#
....#""")
glifo("r", """
....
....
#.##
##..
#...
#...
#...""")
glifo("s", """
.....
.....
.####
#....
.###.
....#
####.""")
glifo("t", """
.#..
.#..
####
.#..
.#..
.#..
..##""")
glifo("u", """
.....
.....
#...#
#...#
#...#
#...#
.####""")
glifo("v", """
.....
.....
#...#
#...#
#...#
.#.#.
..#..""")
glifo("w", """
.....
.....
#...#
#...#
#.#.#
#.#.#
.#.#.""")
glifo("x", """
.....
.....
#...#
.#.#.
..#..
.#.#.
#...#""")
glifo("y", """
.....
.....
#...#
#...#
#...#
.####
....#
....#
.###.""")
glifo("z", """
.....
.....
#####
...#.
..#..
.#...
#####""")

glifo("0", """
.###.
#...#
#..##
#.#.#
##..#
#...#
.###.""")
glifo("1", """
.#.
##.
.#.
.#.
.#.
.#.
###""")
glifo("2", """
.###.
#...#
....#
...#.
..#..
.#...
#####""")
glifo("3", """
####.
....#
....#
.###.
....#
....#
####.""")
glifo("4", """
...#.
..##.
.#.#.
#..#.
#####
...#.
...#.""")
glifo("5", """
#####
#....
####.
....#
....#
#...#
.###.""")
glifo("6", """
.###.
#....
#....
####.
#...#
#...#
.###.""")
glifo("7", """
#####
....#
...#.
..#..
.#...
.#...
.#...""")
glifo("8", """
.###.
#...#
#...#
.###.
#...#
#...#
.###.""")
glifo("9", """
.###.
#...#
#...#
.####
....#
....#
.###.""")

glifo(".", "\n.\n.\n.\n.\n.\n.\n#")
glifo(",", "\n..\n..\n..\n..\n..\n.#\n.#\n#.")
glifo(":", "\n.\n.\n#\n.\n.\n#\n.")
glifo(";", "\n..\n..\n.#\n..\n..\n.#\n.#\n#.")
glifo("!", "\n#\n#\n#\n#\n#\n.\n#")
glifo("¡", "\n#\n.\n#\n#\n#\n#\n#")
glifo("?", """
.###.
#...#
....#
...#.
..#..
.....
..#..""")
glifo("¿", """
..#..
.....
..#..
.#...
#....
#...#
.###.""")
glifo("'", "\n#\n#")
glifo('"', "\n#.#\n#.#")
glifo("-", "\n....\n....\n....\n####")
glifo("—", "\n......\n......\n......\n######")
glifo("(", "\n.#\n#.\n#.\n#.\n#.\n#.\n.#")
glifo(")", "\n#.\n.#\n.#\n.#\n.#\n.#\n#.")
glifo("/", """
....#
...#.
...#.
..#..
.#...
.#...
#....""")
glifo("+", """
.....
..#..
..#..
#####
..#..
..#..""")
glifo("=", "\n.....\n.....\n#####\n.....\n#####")
glifo("…", "\n.....\n.....\n.....\n.....\n.....\n.....\n#.#.#")
glifo("<", "\n...#\n..#.\n.#..\n#...\n.#..\n..#.\n...#")
glifo(">", "\n#...\n.#..\n..#.\n...#\n..#.\n.#..\n#...")

# Tildes y eñes: se arman sobre la letra base.
def con_marca(ch, base, marca, filas_marca):
    desde, filas = G[base]
    ancho = len(filas[0])
    marca_filas = [m.ljust(ancho, ".")[:ancho] for m in marca]
    if desde == 0 and filas[0].strip(".") == "" and filas[1].strip(".") == "":
        # minúscula: la marca ocupa las filas 0-1 vacías
        nuevas = marca_filas + filas[len(marca_filas):]
        G[ch] = (0, nuevas)
    else:
        G[ch] = (-filas_marca, marca_filas + filas)


for base, acento in (("a", "á"), ("e", "é"), ("o", "ó"), ("u", "ú")):
    con_marca(acento, base, ["...#.", "..#.."], 2)
G["í"] = (0, [".#", "#.", "#.", "#.", "#.", "#.", "#."])
con_marca("ñ", "n", [".##.#", "#.##."], 2)
con_marca("ü", "u", [".#.#."], 1)
for base, acento in (("A", "Á"), ("E", "É"), ("O", "Ó"), ("U", "Ú")):
    con_marca(acento, base, ["...#.", "..#.."], 2)
con_marca("Í", "I", [".#.", "#.."], 2)
con_marca("Ñ", "N", [".##.#", "#.##."], 2)


def main():
    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    salida.mkdir(parents=True, exist_ok=True)
    blanco, sombra = (255, 255, 255, 255), (18, 16, 20, 255)
    arriba = 2  # filas reservadas para tildes de mayúsculas
    alto_celda = 11 + 1  # + sombra
    atlas_w = 256
    x = y = 1
    entradas = []
    atlas = Image.new("RGBA", (atlas_w, 128), (0, 0, 0, 0))
    for ch in sorted(G, key=ord):
        desde, filas = G[ch]
        ancho = max(len(f) for f in filas)
        w, h = ancho + 1, alto_celda
        if x + w + 1 > atlas_w:
            x, y = 1, y + h + 1
        celda = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for j, fila in enumerate(filas):
            for i, p in enumerate(fila):
                if p == "#":
                    fy = j + desde + arriba
                    celda.putpixel((i + 1, fy + 1), sombra) if celda.getpixel(
                        (i + 1, fy + 1))[3] == 0 else None
        for j, fila in enumerate(filas):
            for i, p in enumerate(fila):
                if p == "#":
                    celda.putpixel((i, j + desde + arriba), blanco)
        atlas.alpha_composite(celda, (x, y))
        entradas.append((ord(ch), x, y, w, h, ancho + 1))
        x += w + 1
    # espacio
    entradas.append((32, 0, 0, 0, 0, 3))
    atlas.save(salida / "toonaria_fuente.png")
    lineas = [
        'info face="Toonaria" size=11 bold=0 italic=0 charset="" unicode=1 stretchH=100 '
        'smooth=0 aa=1 padding=0,0,0,0 spacing=1,1 outline=0',
        f"common lineHeight=13 base={arriba + 7} scaleW={atlas_w} scaleH=128 pages=1 packed=0",
        'page id=0 file="toonaria_fuente.png"',
        f"chars count={len(entradas)}",
    ]
    for (cid, cx, cy, w, h, adv) in sorted(entradas):
        lineas.append(f"char id={cid} x={cx} y={cy} width={w} height={h} xoffset=0 "
                      f"yoffset=0 xadvance={adv} page=0 chnl=15")
    (salida / "toonaria_fuente.fnt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(len(entradas), "glifos")


if __name__ == "__main__":
    main()
