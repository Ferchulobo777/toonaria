"""Genera por código los assets de pixel art que son geometría pura: tiles de cada nivel,
HUD, proyectiles, efectos, faroles de checkpoint y objetos para recoger.

Se dibujan por código porque necesitan exactitud de grilla: los tiles tienen que repetirse
sin costuras, los proyectiles miden unos pocos píxeles y los efectos tienen que crecer de forma
pareja cuadro a cuadro.

Uso: python objetos_juego.py <carpeta_assets_pixel>
"""

import math
import random
import sys
from pathlib import Path

import numpy as np

from lienzo import Lienzo, tramado

SALIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("salida")


# ---------------------------------------------------------------- tiles

def muro_ladrillos(colores, semilla, ancho=32, alto=32, lad=(16, 8)):
    """Relleno de muro de ladrillos trabados, repetible en ambos ejes."""
    junta, ladrillo, luz, sombra = colores
    rnd = random.Random(semilla)
    c = Lienzo(ancho, alto)
    c.rect(0, 0, ancho - 1, alto - 1, junta)
    lw, lh = lad
    for fila in range(alto // lh):
        desplaz = (lw // 2) * (fila % 2)
        for col in range(-1, ancho // lw + 1):
            x0 = col * lw + desplaz
            y0 = fila * lh
            # Cada ladrillo deja 1 px de junta abajo y a la derecha.
            for x in range(x0, x0 + lw - 1):
                for y in range(y0, y0 + lh - 1):
                    c.px(x % ancho, y, ladrillo)
            for x in range(x0, x0 + lw - 1):
                c.px(x % ancho, y0, luz)
            c.px(x0 % ancho, y0 + 1, luz)
            for x in range(x0 + 1, x0 + lw - 1):
                c.px(x % ancho, y0 + lh - 2, sombra)
            # Textura: algunas marcas de desgaste, siempre dentro del ladrillo.
            for _ in range(rnd.randint(0, 2)):
                mx = x0 + rnd.randint(2, lw - 4)
                my = y0 + rnd.randint(2, lh - 4)
                c.px(mx % ancho, my, sombra)
    return c


def adoquines(colores, semilla, ancho=32, alto=14):
    """Tira superior de adoquines con cordón: lo que el jugador pisa."""
    junta, piedra, luz, cordon = colores
    rnd = random.Random(semilla)
    c = Lienzo(ancho, alto)
    c.rect(0, 0, ancho - 1, alto - 1, junta)
    c.hline(0, ancho - 1, 0, cordon)
    c.hline(0, ancho - 1, 1, luz)
    for fila, y0 in enumerate((3, 8)):
        desplaz = 4 * (fila % 2)
        for col in range(ancho // 8 + 1):
            x0 = col * 8 + desplaz
            w = 6
            for x in range(x0, x0 + w):
                for y in range(y0, y0 + 4):
                    esquina = (x in (x0, x0 + w - 1)) and (y in (y0, y0 + 3))
                    if not esquina:
                        c.px(x % ancho, y, piedra)
            for x in range(x0 + 1, x0 + w - 1):
                c.px(x % ancho, y0, luz)
            if rnd.random() < 0.3:
                c.px((x0 + rnd.randint(1, 4)) % ancho, y0 + 2, junta)
    c.hline(0, ancho - 1, alto - 1, junta)
    return c


def cornisa(colores, ancho=32, alto=10, mensula=True):
    """Cornisa de piedra atravesable desde abajo (plataforma jumpthru)."""
    tinta, cuerpo, luz, sombra = colores
    c = Lienzo(ancho, alto)
    c.rect(0, 0, ancho - 1, 5, cuerpo)
    c.hline(0, ancho - 1, 0, luz)
    c.hline(0, ancho - 1, 1, luz)
    c.hline(0, ancho - 1, 4, sombra)
    c.hline(0, ancho - 1, 5, tinta)
    for x in range(0, ancho, 8):
        c.px(x, 2, sombra)
    if mensula:
        for x0 in (4, 20):
            c.rect(x0, 6, x0 + 6, 7, sombra)
            c.rect(x0 + 1, 8, x0 + 5, 8, sombra)
            c.hline(x0, x0 + 6, 6, cuerpo)
            c.px(x0 - 1, 6, tinta)
            c.px(x0 + 7, 6, tinta)
            c.hline(x0 + 1, x0 + 5, 9, tinta)
            c.px(x0, 8, tinta)
            c.px(x0 + 6, 8, tinta)
    return c


def tablas(colores, semilla, ancho=32, alto=32):
    """Piso de escenario: tablas de madera horizontales."""
    junta, madera, luz, sombra = colores
    rnd = random.Random(semilla)
    c = Lienzo(ancho, alto)
    c.rect(0, 0, ancho - 1, alto - 1, madera)
    for y0 in range(0, alto, 8):
        c.hline(0, ancho - 1, y0, luz)
        c.hline(0, ancho - 1, y0 + 7, junta)
        corte = rnd.randint(4, ancho - 6) if (y0 // 8) % 2 else (y0 * 3) % ancho
        c.vline(corte, y0, y0 + 6, junta)
        for _ in range(2):
            x = rnd.randint(0, ancho - 4)
            c.hline(x, x + rnd.randint(2, 4), y0 + rnd.randint(2, 5), sombra)
        c.px((corte + 3) % ancho, y0 + 3, junta)  # clavo
    return c


def borde_escenario(ancho=32, alto=14):
    """Borde del escenario con candilejas (las luces del piso de un teatro)."""
    c = Lienzo(ancho, alto)
    c.rect(0, 0, ancho - 1, alto - 1, "levita")
    c.hline(0, ancho - 1, 0, "ambar")
    c.hline(0, ancho - 1, 1, "bronce")
    c.hline(0, ancho - 1, 2, "tinta")
    for x0 in (5, 21):
        c.rect(x0, 4, x0 + 5, 9, "gris_oscuro")
        c.rect(x0 + 1, 5, x0 + 4, 8, "llama")
        c.rect(x0 + 2, 5, x0 + 3, 6, "blanco")
        c.hline(x0, x0 + 5, 10, "tinta")
    c.hline(0, ancho - 1, alto - 1, "tinta")
    return c


def marquesina(ancho=32, alto=10):
    """Plataforma de marquesina de teatro con lamparitas."""
    c = Lienzo(ancho, alto)
    c.rect(0, 0, ancho - 1, 6, "gris_oscuro")
    c.hline(0, ancho - 1, 0, "gris")
    c.hline(0, ancho - 1, 6, "tinta")
    for x in range(2, ancho, 6):
        c.px(x, 3, "llama")
        c.px(x + 1, 3, "ambar")
    for x in range(0, ancho, 4):
        c.vline(x + 1, 7, 8, "gris_oscuro")
        c.px(x + 1, 9, "tinta")
    return c


def grietas_plata(base, semilla, densidad=3):
    """Vetas de tinta de luna sobre un tile: la corrupción del Repintado en el nivel 3."""
    rnd = random.Random(semilla)
    c = base.copia()
    for _ in range(densidad):
        x, y = rnd.randrange(c.w), rnd.randrange(c.h)
        for _ in range(rnd.randint(4, 9)):
            c.px(x % c.w, y % c.h, "plata")
            if rnd.random() < 0.5:
                c.px((x + 1) % c.w, y % c.h, "plata_oscura")
            x += rnd.choice((-1, 0, 1))
            y += rnd.choice((0, 1, 1))
    return c


def rejilla_hierro(ancho=32, alto=32):
    """Piso de la cima de la torre: rejilla de hierro sobre el mecanismo del reloj."""
    c = Lienzo(ancho, alto)
    c.rect(0, 0, ancho - 1, alto - 1, "levita")
    for x in range(0, ancho, 8):
        c.vline(x, 0, alto - 1, "gris_oscuro")
        c.vline(x + 1, 0, alto - 1, "gris_medio")
    for y in range(0, alto, 8):
        c.hline(0, ancho - 1, y, "gris_oscuro")
        c.hline(0, ancho - 1, y + 1, "gris_medio")
    for x in range(0, ancho, 8):
        for y in range(0, alto, 8):
            c.px(x + 1, y + 1, "gris_claro")
    return c


def borde_torre(ancho=32, alto=14):
    c = Lienzo(ancho, alto)
    c.rect(0, 0, ancho - 1, alto - 1, "gris_oscuro")
    c.hline(0, ancho - 1, 0, "gris_claro")
    c.hline(0, ancho - 1, 1, "gris")
    c.hline(0, ancho - 1, 3, "tinta")
    for x in range(3, ancho, 8):
        c.rect(x, 6, x + 1, 7, "gris")
        c.px(x, 6, "gris_claro")
    c.hline(0, ancho - 1, alto - 1, "tinta")
    return c


def engranaje_cornisa(ancho=32, alto=10):
    """Cornisa de bronce con dientes de engranaje (nivel 3, cerca del reloj central)."""
    c = Lienzo(ancho, alto)
    c.rect(0, 0, ancho - 1, 5, "bronce")
    c.hline(0, ancho - 1, 0, "llama")
    c.hline(0, ancho - 1, 1, "ambar")
    c.hline(0, ancho - 1, 5, "tinta")
    for x in range(0, ancho, 4):
        c.rect(x + 1, 6, x + 2, 7, "bronce")
        c.hline(x + 1, x + 2, 8, "tinta")
    for x in (7, 23):
        c.px(x, 3, "tinta")
        c.px(x + 1, 3, "llama")
    return c


def generar_tiles():
    d = SALIDA / "tiles"
    piedra = ("levita", "gris_oscuro", "gris_medio", "tinta")
    muro_ladrillos(piedra, 11).guardar(d / "n1_suelo.png")
    adoquines(("tinta", "gris_medio", "gris", "gris_claro"), 12).guardar(d / "n1_borde.png")
    cornisa(("tinta", "gris", "gris_claro", "gris_medio")).guardar(d / "n1_cornisa.png")

    tablas(("tinta", "gris_oscuro", "bronce", "levita"), 21).guardar(d / "n2_suelo.png")
    borde_escenario().guardar(d / "n2_borde.png")
    marquesina().guardar(d / "n2_cornisa.png")

    muro = muro_ladrillos(piedra, 31)
    grietas_plata(muro, 32, densidad=3).guardar(d / "n3_suelo.png")
    grietas_plata(adoquines(("tinta", "gris_medio", "gris", "gris_claro"), 33), 34, 2).guardar(
        d / "n3_borde.png")
    engranaje_cornisa().guardar(d / "n3_cornisa.png")

    rejilla_hierro().guardar(d / "torre_suelo.png")
    borde_torre().guardar(d / "torre_borde.png")
    cornisa(("tinta", "gris_medio", "gris", "gris_oscuro"), mensula=False).guardar(
        d / "torre_cornisa.png")

    # Tile neutro para el prólogo (interior de la carpa): tablas oscuras gastadas.
    # La carpa es un recuerdo de día, en sepia: piso y cajones de madera cálida (bronce y
    # ámbar), no los grises de la ciudad de noche.
    tablas(("tinta", "bronce", "ambar", "levita"), 41).guardar(d / "carpa_suelo.png")
    c = Lienzo(32, 14)
    c.rect(0, 0, 31, 13, "bronce")
    c.hline(0, 31, 0, "crema")
    c.hline(0, 31, 1, "crema_sombra")
    for x in range(0, 32, 8):
        c.rect(x + 2, 4, x + 5, 7, "morado_oscuro")  # alfombra con rombos
        c.px(x + 3, 5, "morado")
        c.px(x + 4, 6, "morado")
    c.hline(0, 31, 13, "tinta")
    c.guardar(d / "carpa_borde.png")
    cornisa(("tinta", "crema_sombra", "crema", "bronce"), mensula=False).guardar(
        d / "carpa_cornisa.png")


# ---------------------------------------------------------------- proyectiles

def carta(ancho_visible, cara, nivel):
    """Carta lunar girando. ancho_visible simula el giro sobre su eje vertical."""
    w, h = 14, 17
    c = Lienzo(w, h)
    cw, ch = ancho_visible, 10
    x0 = (w - cw) // 2
    y0 = (h - ch) // 2
    if cw <= 1:
        c.vline(w // 2, y0, y0 + ch - 1, "morado_claro")
    else:
        c.rect(x0, y0, x0 + cw - 1, y0 + ch - 1, "morado" if cara else "morado_oscuro")
        if cw >= 5:
            if cara:
                # Luna creciente en el frente.
                c.px(x0 + cw // 2, y0 + 3, "luna")
                c.px(x0 + cw // 2 - 1, y0 + 4, "luna")
                c.px(x0 + cw // 2 - 1, y0 + 5, "luna")
                c.px(x0 + cw // 2, y0 + 6, "luna")
            else:
                for yy in range(y0 + 1, y0 + ch - 1, 2):
                    c.px(x0 + 1 + (yy % 4 == 1), yy, "morado")
                    c.px(x0 + cw - 2 - (yy % 4 == 1), yy, "morado")
        c.hline(x0, x0 + cw - 1, y0, "morado_claro")
    c.contorno("tinta")
    if nivel >= 2:
        c.contorno("morado_claro" if nivel == 2 else "luna")
    if nivel >= 3:
        # Aura de carga completa: brillos sueltos alrededor.
        for (px, py) in ((1, 2), (12, 5), (2, 14), (11, 13)):
            c.px(px, py, "blanco")
    return c


def generar_proyectiles():
    d = SALIDA / "proyectiles"
    secuencia = [(7, True), (5, True), (1, True), (5, False)]
    for nivel in (1, 2, 3):
        for i, (w, cara) in enumerate(secuencia):
            carta(w, cara, nivel).guardar(d / f"Carta{nivel}_{i + 1}.png")

    # Farol-bomba: el farol de Ambrosio girando en el aire.
    base = Lienzo(12, 14)
    base.rect(4, 0, 7, 0, "ambar")        # asa
    base.px(3, 1, "ambar")
    base.px(8, 1, "ambar")
    base.rect(2, 2, 9, 3, "bronce")       # tapa
    base.rect(3, 4, 8, 10, "gris_oscuro")  # marco
    base.rect(4, 5, 7, 9, "ambar")        # vidrio iluminado
    base.rect(5, 6, 6, 8, "llama")
    base.px(5, 6, "blanco")
    base.rect(2, 11, 9, 12, "bronce")     # base
    base.contorno("tinta")
    for i in range(4):
        rot = Lienzo(14, 14)
        arr = np.rot90(base.a, -i)
        rot.pegar(arr, (14 - arr.shape[1]) // 2, (14 - arr.shape[0]) // 2)
        rot.guardar(d / f"FarolBomba_{i + 1}.png")


# ---------------------------------------------------------------- efectos

def estallido(radio_max, cuadros, colores, tam, puntas=8, semilla=0):
    """Estallido radial que crece y se desvanece (impacto de carta, parry, chispas)."""
    rnd = random.Random(semilla)
    resultado = []
    for k in range(cuadros):
        t = (k + 1) / cuadros
        c = Lienzo(tam, tam)
        cx = cy = tam // 2
        r = radio_max * (0.35 + 0.65 * t)
        if t < 0.6:
            c.elipse(cx - 0.5, cy - 0.5, r * 0.45 * (1 - t), r * 0.45 * (1 - t), colores[0])
        for p in range(puntas):
            ang = 2 * math.pi * p / puntas + rnd.uniform(-0.15, 0.15)
            largo = r * (1.0 if p % 2 == 0 else 0.65)
            ini = r * 0.35 * t
            x0, y0 = cx + math.cos(ang) * ini, cy + math.sin(ang) * ini
            x1, y1 = cx + math.cos(ang) * largo, cy + math.sin(ang) * largo
            color = colores[1] if t < 0.75 else colores[2]
            c.linea(round(x0), round(y0), round(x1), round(y1), color)
        resultado.append(c)
    return resultado


def explosion_fuego(cuadros=8, tam=48):
    """Explosión del farol: bola de fuego ámbar que termina en humo de tinta."""
    rnd = random.Random(7)
    res = []
    for k in range(cuadros):
        t = k / (cuadros - 1)
        c = Lienzo(tam, tam)
        cx, cy = tam / 2 - 0.5, tam / 2 + 2
        if t < 0.55:
            r = 6 + 16 * (t / 0.55)
            c.elipse(cx, cy, r, r * 0.9, "bronce")
            c.elipse(cx, cy - 1, r * 0.8, r * 0.72, "ambar")
            c.elipse(cx, cy - 2, r * 0.55, r * 0.5, "llama")
            if t < 0.3:
                c.elipse(cx, cy - 2, r * 0.3, r * 0.28, "blanco")
            # bordes irregulares: lenguas de fuego
            for _ in range(10):
                a = rnd.uniform(0, 2 * math.pi)
                x, y = cx + math.cos(a) * r, cy + math.sin(a) * r * 0.9
                c.elipse(x, y, 2.5, 2.5, "ambar")
        else:
            u = (t - 0.55) / 0.45
            for _ in range(7):
                a = rnd.uniform(0, 2 * math.pi)
                d = 10 + 10 * u
                x, y = cx + math.cos(a) * d, cy - 4 * u + math.sin(a) * d * 0.7
                rr = 5 * (1 - u) + 1
                c.elipse(x, y, rr, rr, "gris_oscuro" if u < 0.6 else "gris_medio")
            if u < 0.5:
                c.elipse(cx, cy, 6 * (1 - u), 5 * (1 - u), "bronce")
        c.contorno("tinta")
        res.append(c)
    return res


def polvo(cuadros=4):
    res = []
    for k in range(cuadros):
        c = Lienzo(20, 10)
        t = k / (cuadros - 1)
        for lado in (-1, 1):
            x = 10 + lado * (3 + 6 * t)
            r = 3.2 - 2.2 * t
            c.elipse(x, 7 - 2 * t, r, r * 0.8, "gris_claro" if t < 0.5 else "gris")
        res.append(c)
    return res


def salpicadura_tinta(cuadros=6):
    """Muerte de un Repintado: la tinta salta y se evapora en destellos de plata."""
    rnd = random.Random(5)
    gotas = [(rnd.uniform(-1, 1), rnd.uniform(-1.4, -0.2), rnd.uniform(1.5, 3)) for _ in range(9)]
    res = []
    for k in range(cuadros):
        t = (k + 1) / cuadros
        c = Lienzo(36, 30)
        for (vx, vy, r) in gotas:
            x = 18 + vx * 14 * t
            y = 22 + vy * 16 * t + 14 * t * t
            rr = r * (1 - 0.6 * t)
            if t < 0.8:
                c.elipse(x, y, rr, rr, "tinta")
            else:
                c.px(round(x), round(y), "plata")
        if t < 0.5:
            c.elipse(18, 24, 8 * (1 - t), 3, "tinta")
        if t > 0.4:
            for (vx, vy, _) in gotas[::2]:
                c.px(round(18 + vx * 10 * t), round(20 + vy * 12 * t), "plata")
        res.append(c)
    return res


def destello(cuadros=4):
    res = []
    for k in range(cuadros):
        c = Lienzo(9, 9)
        largo = [1, 3, 4, 2][k % 4]
        for d in range(-largo, largo + 1):
            c.px(4 + d, 4, "luna")
            c.px(4, 4 + d, "luna")
        c.px(4, 4, "blanco")
        if k == 2:
            for d in (-1, 1):
                c.px(4 + d, 4 + d, "morado_claro")
                c.px(4 + d, 4 - d, "morado_claro")
        res.append(c)
    return res


def anillo_parry(cuadros=5):
    res = []
    for k in range(cuadros):
        t = (k + 1) / cuadros
        c = Lienzo(40, 40)
        r = 6 + 13 * t
        c.elipse(19.5, 19.5, r, r, "blanco" if t < 0.5 else "luna", relleno=False)
        if t < 0.7:
            c.elipse(19.5, 19.5, r - 2, r - 2, "morado_claro", relleno=False)
        if t < 0.4:
            # luna creciente en el centro del destello
            c.elipse(19.5, 19.5, 4, 4, "luna")
            c.elipse(21, 18.5, 3.5, 3.5, (0, 0, 0, 0))
        res.append(c)
    return res


def onda_aullido(cuadros=6):
    """Onda expansiva del Aullido del jefe: un arco de luz de luna a ras del piso."""
    res = []
    for k in range(cuadros):
        c = Lienzo(48, 40)
        alto = 10 + 20 * (k % 3) / 2
        c.elipse(24, 39, 22, alto, "plata", relleno=False)
        c.elipse(24, 39, 19, alto - 3, "luna", relleno=False)
        for x in range(4, 44, 6):
            c.px(x + (k % 2) * 3, 39 - int(alto * 0.4), "blanco")
        res.append(c)
    return res


def onda_suelo(cuadros=4):
    """Onda del garrotazo del Agente: más baja y corta que la del jefe (se salta con un salto
    simple), en plata y no en luna, para que no se confunda con la magia del Aullido."""
    res = []
    for k in range(cuadros):
        c = Lienzo(32, 20)
        alto = 8 + 6 * (k % 2)
        c.elipse(16, 19, 14, alto, "plata_oscura", relleno=False)
        c.elipse(16, 19, 12, alto - 2, "plata", relleno=False)
        for x in range(5, 28, 5):
            c.px(x + (k % 2) * 2, 19 - int(alto * 0.5), "blanco")
        res.append(c)
    return res


def garra_luna(cuadros=4):
    """Proyectil del jefe: medialuna morada con estela (misma magia que las cartas)."""
    res = []
    for k in range(cuadros):
        c = Lienzo(20, 16)
        c.elipse(9, 8, 6, 6, "morado")
        c.elipse(11, 7, 5.5, 5.5, (0, 0, 0, 0))
        c.elipse(9, 8, 6, 6, "morado_claro", relleno=False)
        c.elipse(11, 7, 5.5, 5.5, (0, 0, 0, 0))
        for i in range(3):
            c.px(15 + i, 6 + (i + k) % 4, "morado_claro" if i < 2 else "luna")
        c.contorno("tinta")
        res.append(c)
    return res


def generar_efectos():
    d = SALIDA / "fx"
    for i, c in enumerate(estallido(10, 5, ("blanco", "morado_claro", "morado"), 24, 8, 1)):
        c.guardar(d / f"Impacto_{i + 1}.png")
    for i, c in enumerate(explosion_fuego()):
        c.guardar(d / f"Explosion_{i + 1}.png")
    for i, c in enumerate(polvo()):
        c.guardar(d / f"Polvo_{i + 1}.png")
    for i, c in enumerate(salpicadura_tinta()):
        c.guardar(d / f"Tinta_{i + 1}.png")
    for i, c in enumerate(destello()):
        c.guardar(d / f"Destello_{i + 1}.png")
    for i, c in enumerate(anillo_parry()):
        c.guardar(d / f"Parry_{i + 1}.png")
    for i, c in enumerate(estallido(5, 3, ("blanco", "blanco", "gris_claro"), 12, 6, 3)):
        c.guardar(d / f"Chispa_{i + 1}.png")
    for i, c in enumerate(onda_aullido()):
        c.guardar(d / f"OndaAullido_{i + 1}.png")
    for i, c in enumerate(onda_suelo()):
        c.guardar(d / f"OndaSuelo_{i + 1}.png")
    for i, c in enumerate(garra_luna()):
        c.guardar(SALIDA / "proyectiles" / f"GarraLuna_{i + 1}.png")


# ---------------------------------------------------------------- objetos del nivel

def farol_gas(encendido, cuadro=0):
    """Farol de gas de Ambrosio: el checkpoint. Apagado o encendido (llama que titila)."""
    c = Lienzo(24, 60)
    cx = 12
    # poste
    c.rect(cx - 1, 18, cx + 1, 55, "levita")
    c.vline(cx - 1, 18, 55, "gris_oscuro")
    c.rect(cx - 3, 54, cx + 3, 57, "gris_oscuro")
    c.hline(cx - 3, cx + 3, 54, "gris_medio")
    c.rect(cx - 4, 58, cx + 4, 59, "levita")
    c.rect(cx - 2, 30, cx + 2, 31, "gris_oscuro")  # anillo decorativo
    c.rect(cx - 6, 17, cx + 6, 18, "gris_oscuro")  # travesaño
    # cabeza del farol
    c.rect(cx - 5, 5, cx + 5, 6, "gris_oscuro")
    c.rect(cx - 3, 3, cx + 3, 4, "gris_oscuro")
    c.rect(cx - 1, 1, cx + 1, 2, "gris_medio")
    c.rect(cx - 4, 7, cx + 4, 15, "gris_oscuro")
    if encendido:
        brillo = ["llama", "ambar", "llama", "blanco"][cuadro % 4]
        c.rect(cx - 3, 8, cx + 3, 14, "ambar")
        c.rect(cx - 2, 9 + (cuadro % 2), cx + 2, 14, "llama")
        c.rect(cx - 1, 10 + (cuadro % 2), cx + 1, 13, brillo)
    else:
        c.rect(cx - 3, 8, cx + 3, 14, "gris_medio")
        c.px(cx - 2, 9, "gris_claro")
        c.px(cx - 2, 10, "gris_claro")
    c.vline(cx, 7, 15, "gris_oscuro")  # parante central del vidrio
    c.rect(cx - 5, 15, cx + 5, 16, "gris_oscuro")
    c.contorno("tinta")
    if encendido:
        # Halo de luz con trama: el resplandor no puede ser semitransparente en esta paleta.
        for y in range(2, 22):
            for x in range(0, 24):
                d = math.hypot(x - cx, (y - 11) * 1.2)
                if 8 < d < 11.5 and c.a[y, x, 3] == 0 and (x + y + cuadro) % 3 == 0:
                    c.px(x, y, "ambar" if d < 10 else "bronce")
    return c


def taza_te(cuadro):
    """El té de Ambrosio (la pava que nunca deja de hervir): recupera vida."""
    c = Lienzo(14, 16)
    c.rect(1, 13, 12, 14, "gris_claro")   # plato
    c.hline(2, 11, 15, "gris")
    c.rect(3, 8, 10, 12, "blanco")        # taza
    c.hline(3, 10, 12, "gris_claro")
    c.rect(4, 9, 9, 9, "bronce")          # té
    c.rect(11, 9, 12, 11, "blanco")       # asa
    c.px(11, 10, (0, 0, 0, 0))
    c.px(6, 11, "morado")                 # lunita pintada
    c.contorno("tinta")
    for i, y in enumerate((6, 4, 2)):     # vapor ondulante
        x = 6 + ((i + cuadro) % 2) * 2 - 1
        c.px(x, y, "gris_claro")
        c.px(x + 1, y - 1, "gris_claro")
    return c


def fragmento_luna(cuadro):
    """Fragmento de luna: recupera maná."""
    c = Lienzo(12, 12)
    c.elipse(5.5, 5.5, 4, 4, "luna")
    c.elipse(7, 4.5, 3.5, 3.5, (0, 0, 0, 0))
    c.elipse(5.5, 5.5, 4, 4, "morado_claro", relleno=False)
    c.elipse(7, 4.5, 3.5, 3.5, (0, 0, 0, 0))
    c.contorno("morado_oscuro")
    puntos = [(10, 1), (1, 10), (10, 10), (1, 1)]
    x, y = puntos[cuadro % 4]
    c.px(x, y, "blanco")
    return c


def generar_objetos():
    d = SALIDA / "objetos"
    farol_gas(False).guardar(d / "FarolGas_Apagado_1.png")
    for i in range(4):
        farol_gas(True, i).guardar(d / f"FarolGas_Encendido_{i + 1}.png")
    for i in range(2):
        taza_te(i).guardar(d / f"Te_{i + 1}.png")
    for i in range(4):
        fragmento_luna(i).guardar(d / f"Luna_{i + 1}.png")

    # Arco de salida de cada nivel: reja de hierro forjado con una luna en lo alto.
    c = Lienzo(48, 72)
    c.rect(2, 10, 45, 71, "levita")
    c.elipse(23.5, 12, 22, 12, "levita")
    c.rect(6, 14, 41, 71, "tinta")
    for x in range(9, 40, 6):
        c.vline(x, 14, 71, "gris_oscuro")
        c.px(x, 13, "gris_medio")
    c.hline(6, 41, 40, "gris_oscuro")
    c.elipse(23.5, 7, 4, 4, "luna")
    c.elipse(25, 6, 3.5, 3.5, "levita")
    c.contorno("tinta")
    c.guardar(d / "Salida_1.png")


# ---------------------------------------------------------------- HUD

def generar_hud(retrato_idle=None):
    d = SALIDA / "hud"
    # Cartas de vida: cada una vale 20 de vida; media carta = 10.
    for estado in ("Llena", "Media", "Vacia"):
        c = Lienzo(11, 14)
        c.rect(1, 1, 9, 12, "gris_oscuro")
        if estado in ("Llena", "Media"):
            hasta = 9 if estado == "Llena" else 5
            c.rect(1, 1, hasta, 12, "morado")
            c.hline(1, hasta, 1, "morado_claro")
            c.px(5, 5, "luna")
            c.px(4, 6, "luna")
            c.px(4, 7, "luna")
            c.px(5, 8, "luna")
        else:
            c.px(5, 5, "gris_medio")
            c.px(4, 6, "gris_medio")
            c.px(4, 7, "gris_medio")
            c.px(5, 8, "gris_medio")
        c.rect(0, 0, 10, 0, "tinta")
        c.rect(0, 13, 10, 13, "tinta")
        c.vline(0, 0, 13, "tinta")
        c.vline(10, 0, 13, "tinta")
        c.guardar(d / f"CartaVida_{estado}_1.png")

    # Marco del retrato
    m = Lienzo(30, 30)
    m.elipse(14.5, 14.5, 14, 14, "tinta")
    m.elipse(14.5, 14.5, 13, 13, "gris_oscuro")
    m.elipse(14.5, 14.5, 11, 11, "levita")
    for a in range(0, 360, 45):
        x = 14.5 + math.cos(math.radians(a)) * 13.5
        y = 14.5 + math.sin(math.radians(a)) * 13.5
        m.px(round(x), round(y), "morado_claro")
    if retrato_idle is not None:
        retrato(m.copia(), retrato_idle).guardar(d / "Retrato_1.png")
    else:
        m.guardar(d / "Retrato_1.png")
    # Retratos de los demás personajes que hablan en los diálogos, con el mismo marco.
    for nombre, carpeta, filas, lado in (("Ambrosio", "ambrosio", 20, None),
                                         ("Actor", "actor", 22, None),
                                         ("Lobo", "lobo", 26, "derecha")):
        idle = SALIDA / carpeta / "Idle_1.png"
        if idle.exists():
            from PIL import Image
            frame = np.asarray(Image.open(idle).convert("RGBA"))
            marco = m.copia()
            if nombre == "Lobo":
                # El lobo es casi negro: sobre el fondo oscuro del marco no se lee la silueta,
                # así que su retrato lleva el fondo morado de la magia lunar.
                marco.elipse(14.5, 14.5, 11, 11, "morado_oscuro")
            retrato(marco, frame, filas, lado).guardar(d / f"Retrato{nombre}_1.png")


def retrato(marco, frame, filas=20, lado=None):
    """Cabeza recortada del primer frame de idle, dentro del marco circular.

    lado="derecha" es para el lobo: está encorvado y lo más alto de la figura es el lomo, así
    que la cabeza se toma de las últimas columnas (mira a la derecha)."""
    ys, xs = np.nonzero(frame[..., 3] > 0)
    top = ys.min()
    cab = frame[top:top + filas]
    cxs = np.nonzero(cab[..., 3].any(0))[0]
    x0, x1 = cxs.min(), cxs.max() + 1
    if lado == "derecha":
        x0 = max(x0, x1 - 24)
    cab = cab[:, x0:x1]
    recorte = Lienzo(30, 30)
    recorte.pegar(cab, 15 - cab.shape[1] // 2, 5 if filas <= 22 else 3)
    circulo = Lienzo(30, 30)
    circulo.elipse(14.5, 14.5, 11, 11, "blanco")
    recorte.a[~circulo.mascara()] = 0
    marco.pegar(recorte, 0, 0)
    return marco

    # Barra de maná: fondo con ícono de luna + relleno de 1 px de ancho (se estira por evento).
    f = Lienzo(64, 8)
    f.rect(0, 0, 63, 7, "tinta")
    f.rect(1, 1, 62, 6, "levita")
    f.rect(2, 2, 61, 5, "gris_oscuro")
    f.guardar(d / "BarraManaFondo_1.png")
    r = Lienzo(1, 4)
    r.px(0, 0, "morado_claro")
    r.rect(0, 1, 0, 3, "morado")
    r.guardar(d / "BarraMana_1.png")
    # Medidor de carga sobre la cabeza de Ventura
    f = Lienzo(24, 5)
    f.rect(0, 0, 23, 4, "tinta")
    f.rect(1, 1, 22, 3, "gris_oscuro")
    f.guardar(d / "BarraCargaFondo_1.png")
    for nombre, col in (("1", "morado_claro"), ("2", "luna"), ("3", "blanco")):
        r = Lienzo(1, 3)
        r.rect(0, 0, 0, 2, col)
        r.guardar(d / f"BarraCarga_{nombre}.png")
    # Barra del jefe
    f = Lienzo(240, 10)
    f.rect(0, 0, 239, 9, "tinta")
    f.rect(1, 1, 238, 8, "levita")
    f.rect(2, 2, 237, 7, "gris_oscuro")
    for x in range(2, 238, 24):
        f.vline(x, 2, 7, "levita")
    f.guardar(d / "BarraJefeFondo_1.png")
    r = Lienzo(1, 6)
    r.px(0, 0, "luna")
    r.rect(0, 1, 0, 3, "plata")
    r.rect(0, 4, 0, 5, "plata_oscura")
    r.guardar(d / "BarraJefe_1.png")
    # Caja de diálogo (se estira con 9-slice: bordes de 6 px)
    c = Lienzo(24, 24)
    c.rect(0, 0, 23, 23, "tinta")
    c.rect(1, 1, 22, 22, "gris_oscuro")
    c.rect(2, 2, 21, 21, "levita")
    c.rect(3, 3, 20, 20, "levita")
    for p in ((1, 1), (22, 1), (1, 22), (22, 22)):
        c.px(*p, "morado_claro")
    c.guardar(d / "CajaDialogo.png")
    # Indicador "seguir" del diálogo
    c = Lienzo(7, 5)
    for i in range(4):
        c.hline(i, 6 - i, i, "luna")
    c.guardar(d / "Seguir_1.png")
    # Píxel negro para fundidos de pantalla
    c = Lienzo(8, 8)
    c.rect(0, 0, 7, 7, "tinta")
    c.guardar(d / "Negro.png")


if __name__ == "__main__":
    from PIL import Image
    idle = SALIDA / "ventura" / "Idle_1.png"
    retrato = np.asarray(Image.open(idle).convert("RGBA")) if idle.exists() else None
    generar_tiles()
    generar_proyectiles()
    generar_efectos()
    generar_objetos()
    generar_hud(retrato)
    print("listo:", sum(1 for _ in SALIDA.rglob("*.png")), "png en", SALIDA)
