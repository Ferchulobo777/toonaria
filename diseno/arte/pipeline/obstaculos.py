"""Obstáculos y plataformas especiales de los niveles, dibujados por código.

Cada obstáculo nace del mundo del juego, no es un pincho genérico:
- Rejas con púas: el hierro forjado de las veredas victorianas.
- Charco de tinta: lo que deja el Repintado al pasar; quema al pisarlo.
- Engranaje: el reloj roto del barrio "escupe" engranajes que caen (ver tramo 3 del nivel 1).
- Toldo elástico: un toldo de negocio que rebota como en un dibujo animado de los años 30.
- Tablón podrido: plataforma que cede al pisarla.
- Barril: se rompe con una carta o con el farol y puede soltar té o fragmentos de luna.
- Péndulo: el péndulo del reloj central (nivel 3), gira sobre su eje superior.
- Andamio: plataforma móvil de madera colgada de sogas.

Uso: python obstaculos.py <carpeta_assets_pixel>
"""

import math
import random
import sys
from pathlib import Path

from lienzo import Lienzo

SALIDA = (Path(sys.argv[1]) if len(sys.argv) > 1 else Path("salida")) / "obstaculos"


def rejas():
    c = Lienzo(32, 20)
    c.hline(0, 31, 13, "gris_oscuro")       # travesaño inferior
    c.hline(0, 31, 8, "gris_oscuro")        # travesaño superior
    for x in range(1, 32, 5):
        c.vline(x, 4, 19, "levita")
        c.vline(x + 1, 5, 19, "gris_oscuro")
        c.px(x, 3, "gris")                  # punta de lanza
        c.px(x + 1, 3, "gris_medio")
        c.px(x, 2, "gris_claro")
        c.px(x - 1, 4, "gris_medio")
        c.px(x + 2, 4, "levita")
    c.contorno("tinta")
    return c


def charco(cuadro):
    c = Lienzo(48, 8)
    c.elipse(23.5, 5, 23, 3.2, "tinta")
    c.elipse(23.5, 4.6, 20, 2.2, "levita")
    rnd = random.Random(cuadro)
    for _ in range(3):  # destellos de plata que se mueven: la tinta "viva"
        x = rnd.randint(6, 40)
        c.px(x, 4, "plata")
        c.px(x + 1, 4, "plata_oscura")
    burbuja = [(10, 2), (30, 1), (20, 2)][cuadro % 3]
    c.px(burbuja[0], burbuja[1], "levita")
    c.px(burbuja[0], burbuja[1] - 1, "tinta")
    return c


def engranaje(angulo, r_ext=11, r_int=8, dientes=8, tam=26, cuerpo="bronce", luz="ambar"):
    c = Lienzo(tam, tam)
    cx = cy = (tam - 1) / 2
    for y in range(tam):
        for x in range(tam):
            dx, dy = x - cx, y - cy
            d = math.hypot(dx, dy)
            a = (math.atan2(dy, dx) - angulo) % (2 * math.pi)
            diente = (a * dientes / (2 * math.pi)) % 1.0 < 0.45
            radio = r_ext if diente else r_int
            if d <= radio:
                c.px(x, y, cuerpo)
                if d < r_int - 1 and (dx + dy) < -2:
                    c.px(x, y, luz)
            if 2.2 < d < 4.2:
                c.px(x, y, "tinta")
            if d <= 2.2:
                c.px(x, y, "levita")
    for k in range(3):  # rayos
        a = angulo + k * 2 * math.pi / 3
        for t in range(4, 8):
            c.px(round(cx + math.cos(a) * t), round(cy + math.sin(a) * t), "tinta")
    c.contorno("tinta")
    return c


def toldo(estado):
    """Toldo rayado. estado: 0 reposo, 1 aplastado, 2 estirado (rebote)."""
    alto = {0: 12, 1: 8, 2: 15}[estado]
    c = Lienzo(52, 20)
    y0 = 20 - alto - 2
    for x in range(2, 50):
        caida = int(3 * math.sin((x - 2) / 47 * math.pi)) if estado == 1 else 0
        franja = "morado" if ((x - 2) // 6) % 2 == 0 else "crema"
        sombra = "morado_oscuro" if franja == "morado" else "crema_sombra"
        for y in range(y0 + caida, 18):
            c.px(x, y, franja if y < 15 else sombra)
        c.px(x, y0 + caida, "morado_claro" if franja == "morado" else "blanco")
    for x in range(2, 50, 6):  # festón inferior
        c.px(x + 2, 18, "morado_oscuro")
        c.px(x + 3, 18, "morado_oscuro")
    c.vline(1, y0, 19, "gris_oscuro")
    c.vline(50, y0, 19, "gris_oscuro")
    c.contorno("tinta")
    return c


def tablon(estado):
    """Tablón podrido: 0 sano, 1 crujiendo (grietas), 2 partiéndose."""
    c = Lienzo(48, 12)
    c.rect(0, 2, 47, 8, "bronce")
    c.hline(0, 47, 2, "ambar")
    c.hline(0, 47, 8, "levita")
    for x in (11, 27, 41):
        c.vline(x, 3, 7, "levita")
        c.px(x + 2, 5, "tinta")  # clavos
    if estado >= 1:
        for (x, y) in ((18, 3), (19, 4), (20, 5), (20, 6), (33, 4), (34, 5)):
            c.px(x, y, "tinta")
    if estado == 2:
        c.rect(22, 2, 24, 9, (0, 0, 0, 0))
        for (x, y) in ((21, 9), (25, 10), (23, 11)):
            c.px(x, y, "bronce")
    c.contorno("tinta")
    return c


def barril(estado):
    c = Lienzo(22, 26)
    if estado == 0:
        c.rect(3, 2, 18, 24, "bronce")
        c.vline(4, 3, 23, "ambar")
        c.vline(10, 2, 24, "levita")
        c.vline(15, 2, 24, "levita")
        for y in (5, 13, 21):
            c.hline(2, 19, y, "gris_oscuro")
            c.hline(3, 18, y - 1, "gris_medio")
        c.rect(6, 0, 15, 1, "bronce")
        c.px(10, 9, "morado")  # luna pintada: barril del puesto de Ambrosio
        c.px(9, 10, "morado")
        c.px(10, 11, "morado")
        c.contorno("tinta")
    else:
        rnd = random.Random(estado)
        for _ in range(7):
            x, y = rnd.randint(1, 18), rnd.randint(8 + estado * 3, 24)
            c.rect(x, y, x + rnd.randint(1, 3), y + 1, rnd.choice(["bronce", "ambar", "gris_oscuro"]))
        c.contorno("tinta")
    return c


def pendulo():
    """Brazo del péndulo con la pesa en forma de medialuna. Origen previsto: el eje (arriba)."""
    c = Lienzo(36, 112)
    c.elipse(17.5, 4, 4, 4, "gris_oscuro")
    c.elipse(17.5, 4, 1.5, 1.5, "ambar")
    c.rect(16, 6, 19, 88, "gris_oscuro")
    c.vline(16, 6, 88, "gris_medio")
    c.elipse(17.5, 96, 17, 14, "bronce")
    c.elipse(17.5, 99, 13, 10, "ambar")
    c.elipse(17.5, 92, 14, 10, (0, 0, 0, 0))   # vaciado: queda una medialuna
    c.elipse(17.5, 100, 9, 5, "llama")
    c.contorno("tinta")
    return c


def andamio():
    c = Lienzo(48, 40)
    for x in (4, 43):
        c.vline(x, 0, 29, "crema_sombra")  # sogas
        c.vline(x + 1, 0, 29, "bronce")
    c.rect(0, 30, 47, 36, "bronce")
    c.hline(0, 47, 30, "ambar")
    c.hline(0, 47, 36, "levita")
    for x in range(8, 47, 10):
        c.vline(x, 31, 35, "levita")
    c.contorno("tinta")
    return c


def nube_obstaculo(cuadro):
    """Nube de tinta flotante sobre la que se puede pararse un momento (nivel 2 y 3)."""
    c = Lienzo(48, 20)
    off = cuadro % 2
    for (x, y, r) in ((12, 11, 7), (24, 8 + off, 9), (36, 11, 7), (18, 13, 6), (30, 13, 6)):
        c.elipse(x, y, r, r * 0.75, "gris_claro")
    for (x, y, r) in ((24, 6 + off, 5), (14, 9, 3)):
        c.elipse(x, y, r, r * 0.6, "blanco")
    for x in range(8, 41):
        if c.a[16, x, 3]:
            c.px(x, 16, "gris")
    c.contorno("tinta")
    return c


def main():
    rejas().guardar(SALIDA / "Rejas.png")
    for i in range(3):
        charco(i).guardar(SALIDA / f"CharcoTinta_{i + 1}.png")
    for i in range(4):
        engranaje(i * math.pi / 16).guardar(SALIDA / f"Engranaje_{i + 1}.png")
    for nombre, est in (("Reposo", 0), ("Aplastado", 1), ("Estirado", 2)):
        toldo(est).guardar(SALIDA / f"Toldo_{nombre}_1.png")
    for i in range(3):
        tablon(i).guardar(SALIDA / f"Tablon_{i + 1}.png")
    barril(0).guardar(SALIDA / "Barril_Entero_1.png")
    for i in range(1, 4):
        barril(i).guardar(SALIDA / f"Barril_Roto_{i}.png")
    pendulo().guardar(SALIDA / "Pendulo_1.png")
    andamio().guardar(SALIDA / "Andamio_1.png")
    for i in range(2):
        nube_obstaculo(i).guardar(SALIDA / f"NubeTinta_{i + 1}.png")
    print("obstáculos listos en", SALIDA)


if __name__ == "__main__":
    main()
