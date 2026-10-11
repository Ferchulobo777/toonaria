"""Efectos de sonido de Toonaria, uno por función.

Criterios de diseño (los mismos de audio-juice-polish de la cátedra):
- Cada acción del jugador tiene respuesta sonora inmediata y corta (salto, carta, parry), con
  ataque casi nulo para que se sienta "pegada" al botón.
- Los avisos de los enemigos (gruñido, silbato, "ta-dá") tienen identidad propia: el jugador
  tiene que poder reconocer QUÉ va a atacar sin mirar.
- Lo que recompensa (té, luna, farol encendido, parry) usa intervalos consonantes hacia arriba;
  lo que castiga (daño, derrota, caída) baja de altura.

Uso: python sonidos.py <carpeta_salida>
"""

import sys
from pathlib import Path

import numpy as np

from sintesis import (SR, adsr, barrido, caida, en, eco, guardar_wav, mezclar, nota, pasaaltos,
                      pasabajos, pulso, ruido, seno, sierra, tiempo, triangulo, vibrato)


def tono(frec, dur, forma=pulso, env=None, **k):
    """Una nota con su envolvente (por defecto, golpe corto)."""
    n = int(dur * SR)
    frec = np.broadcast_to(np.asarray(frec, dtype=np.float64), (n,)) if np.ndim(frec) == 0 else frec[:n]
    x = forma(frec, **k) if k else forma(frec)
    return x * (env if env is not None else adsr(n, 0.002, dur * 0.4, 0.4, dur * 0.4))


def arpegio(notas, paso, forma=pulso, dur_nota=None, **k):
    lienzo = np.zeros(int((paso * len(notas) + (dur_nota or paso) + 0.05) * SR))
    for i, n_ in enumerate(notas):
        d = dur_nota or paso * 1.6
        en(lienzo, tono(nota(n_), d, forma, adsr(int(d * SR), 0.002, d * 0.3, 0.3, d * 0.5), **k), i * paso)
    return lienzo


# --------------------------------------------------------------------- jugador

def salto():
    d = 0.13
    return tono(barrido(300, 640, d), d, pulso, caida(int(d * SR), 0.06), ciclo=0.5) * 0.7


def salto_doble():
    a = tono(barrido(520, 1040, 0.12), 0.12, pulso, caida(int(0.12 * SR), 0.05), ciclo=0.25)
    b = tono(barrido(1300, 2000, 0.1), 0.1, triangulo, caida(int(0.1 * SR), 0.04))
    return mezclar(a * 0.6, np.concatenate([np.zeros(int(0.05 * SR)), b * 0.4]))


def aterrizar():
    n = int(0.09 * SR)
    golpe = pasabajos(ruido(n, 1), 900) * caida(n, 0.025)
    bombo = seno(barrido(110, 50, 0.09)) * caida(n, 0.03)
    return golpe * 0.8 + bombo * 0.6


def carga():
    d = 0.4
    f = vibrato(barrido(220, 440, d), 9, 0.03)
    return tono(f, d, triangulo, adsr(int(d * SR), 0.03, 0.1, 0.7, 0.15)) * 0.5


def carta():
    n = int(0.16 * SR)
    soplo = pasaaltos(pasabajos(ruido(n, 2), barrido(4000, 1500, 0.16)), 600) * caida(n, 0.05)
    blip = tono(barrido(1100, 700, 0.08), 0.08, pulso, caida(int(0.08 * SR), 0.03), ciclo=0.125)
    return mezclar(soplo * 0.7, blip * 0.35)


def farol():
    n = int(0.2 * SR)
    soplo = pasabajos(ruido(n, 3), 1800) * caida(n, 0.08)
    vidrio = tono(nota("E6"), 0.25, triangulo, caida(int(0.25 * SR), 0.06))
    return mezclar(soplo * 0.6, np.concatenate([np.zeros(int(0.04 * SR)), vidrio * 0.35]))


def explosion():
    d = 0.9
    n = int(d * SR)
    estallido = pasabajos(ruido(n, 4, periodo=2), barrido(5000, 200, d)) * caida(n, 0.22)
    bombo = seno(barrido(90, 28, d)) * caida(n, 0.25)
    return estallido * 0.9 + bombo * 0.8


def parry_aire():
    n = int(0.11 * SR)
    return pasaaltos(ruido(n, 5), 2500) * adsr(n, 0.01, 0.03, 0.5, 0.06) * 0.5


def parry():
    d = 0.5
    n = int(d * SR)
    a = pulso(np.full(n, nota("E6")), 0.25) * caida(n, 0.12)
    b = pulso(np.full(n, nota("B6")), 0.5) * caida(n, 0.09)
    brillo = triangulo(np.full(n, nota("E7"))) * caida(n, 0.2)
    return eco(a * 0.35 + b * 0.25 + brillo * 0.3, 0.09, 0.4, 0.4, 0.4)


def dano():
    d = 0.22
    n = int(d * SR)
    golpe = pulso(barrido(240, 90, d), 0.5) * caida(n, 0.08)
    ras = pasabajos(ruido(n, 6), 2500) * caida(n, 0.04)
    return golpe * 0.6 + ras * 0.5


def derrota():
    x = arpegio(["A4", "F4", "D4", "A3"], 0.2, pulso, 0.35, ciclo=0.5)
    return eco(x * 0.6, 0.2, 0.3, 0.3, 0.6)


def caida_pozo():
    d = 0.55
    return tono(barrido(900, 160, d), d, seno, adsr(int(d * SR), 0.01, 0.1, 0.8, 0.15)) * 0.6


# --------------------------------------------------------------------- enemigos

def gruñido(base=85, dur=0.45, semilla=7):
    n = int(dur * SR)
    t = tiempo(dur)
    voz = sierra(vibrato(np.full(n, float(base)), 7, 0.06)) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t))
    aire = pasabajos(ruido(n, semilla), 700)
    return pasabajos(voz * 0.7 + aire * 0.5, 1200) * adsr(n, 0.04, 0.1, 0.8, 0.12)


def repintado_aviso():
    return gruñido(120, 0.35, 8) * 0.8


def golpe():
    n = int(0.12 * SR)
    seco = pasabajos(ruido(n, 9), 3000) * caida(n, 0.03)
    cuerpo = pulso(barrido(170, 80, 0.12), 0.5) * caida(n, 0.05)
    return seco * 0.7 + cuerpo * 0.5


def tinta():
    d = 0.45
    n = int(d * SR)
    t = tiempo(d)
    burbuja = triangulo(barrido(320, 120, d) * (1 + 0.25 * np.sin(2 * np.pi * 18 * t))) * caida(n, 0.15)
    chapoteo = pasabajos(ruido(n, 10), 1200) * caida(n, 0.07)
    return burbuja * 0.6 + chapoteo * 0.5


def actor_aviso():
    # "¡Ta-dá!": dos notas de fanfarria, el Actor anuncia su número antes de tirar.
    return arpegio(["G4", "C5"], 0.11, pulso, 0.16, ciclo=0.25) * 0.6


def mascara():
    d = 0.3
    n = int(d * SR)
    t = tiempo(d)
    risita = triangulo(np.where((t * 22) % 1 < 0.5, nota("A5"), nota("C6"))) * adsr(n, 0.01, 0.1, 0.5, 0.1)
    soplo = pasaaltos(ruido(n, 11), 1800) * caida(n, 0.08)
    return risita * 0.35 + soplo * 0.4


def cuervo():
    lienzo = np.zeros(int(0.5 * SR))
    for i in range(2):
        d = 0.16
        n = int(d * SR)
        graznido = sierra(barrido(720, 420, d)) + 0.5 * pulso(barrido(1440, 840, d), 0.3)
        en(lienzo, pasabajos(graznido, 2200) * adsr(n, 0.01, 0.04, 0.7, 0.05), i * 0.2)
    return lienzo * 0.5


def agente_aviso():
    # Silbato de policía: tono agudo con trino rápido.
    d = 0.42
    n = int(d * SR)
    t = tiempo(d)
    f = 2300 * (1 + 0.035 * np.sign(np.sin(2 * np.pi * 26 * t)))
    return seno(f) * adsr(n, 0.01, 0.05, 0.8, 0.08) * 0.45


def golpe_suelo():
    d = 0.6
    n = int(d * SR)
    bombo = seno(barrido(80, 30, d)) * caida(n, 0.18)
    tierra = pasabajos(ruido(n, 12, periodo=3), 600) * caida(n, 0.14)
    return bombo * 0.9 + tierra * 0.7


def bloqueo():
    d = 0.18
    n = int(d * SR)
    return (pulso(np.full(n, nota("D6")), 0.125) * caida(n, 0.03) * 0.4
            + pasaaltos(ruido(n, 13), 4000) * caida(n, 0.015) * 0.5)


# --------------------------------------------------------------------- jefe

def grunido():
    return gruñido(70, 0.65, 14)


def embestida():
    lienzo = np.zeros(int(0.55 * SR))
    for i in range(4):
        n = int(0.08 * SR)
        en(lienzo, seno(barrido(90, 45, 0.08)) * caida(n, 0.03), i * 0.12)
    n = lienzo.size
    return lienzo * 0.8 + pasabajos(ruido(n, 15), barrido(400, 2500, 0.55)) * adsr(n, 0.2, 0.1, 0.7, 0.2) * 0.4


def golpe_pared():
    d = 0.75
    n = int(d * SR)
    choque = pasabajos(ruido(n, 16, periodo=2), barrido(6000, 300, d)) * caida(n, 0.15)
    bombo = seno(barrido(70, 25, d)) * caida(n, 0.3)
    metal = pulso(np.full(n, 190.0), 0.3) * caida(n, 0.08)
    return choque * 0.8 + bombo * 0.9 + metal * 0.25


def zarpazo():
    d = 0.24
    n = int(d * SR)
    corte = pasaaltos(pasabajos(ruido(n, 17), barrido(8000, 1500, d)), 900)
    return corte * adsr(n, 0.005, 0.06, 0.5, 0.12) * 0.8


def garra_carga():
    d = 0.7
    f = vibrato(barrido(180, 520, d), 11, 0.04)
    n = int(d * SR)
    return pasabajos(sierra(f), 1800) * adsr(n, 0.15, 0.1, 0.8, 0.12) * 0.5


def garra():
    d = 0.22
    n = int(d * SR)
    t = tiempo(d)
    return (pulso(barrido(1000, 380, d), 0.25) * (0.7 + 0.3 * np.sin(2 * np.pi * 40 * t))
            * caida(n, 0.09) * 0.45)


def aullido():
    d = 1.3
    n = int(d * SR)
    t = tiempo(d)
    curva = np.interp(t, [0, 0.25, 0.9, 1.3], [300, 620, 560, 380])
    voz = sierra(vibrato(curva, 5.5, 0.025, 0.2)) * 0.5 + seno(vibrato(curva, 5.5, 0.025, 0.2)) * 0.5
    return eco(pasabajos(voz, 2400) * adsr(n, 0.12, 0.2, 0.85, 0.35) * 0.6, 0.23, 0.35, 0.35, 0.8)


def transicion():
    d = 1.4
    n = int(d * SR)
    acorde = sum(triangulo(vibrato(np.full(n, nota(x)), 4 + i, 0.01)) for i, x in enumerate(["E3", "G3", "Bb3", "Db4"]))
    oleaje = np.linspace(0, 1, n) ** 2
    return eco(acorde * oleaje * adsr(n, 0.01, 0.1, 1, 0.2) * 0.25, 0.3, 0.4, 0.4, 0.8)


def derrota_jefe():
    choque = golpe_pared()
    lamento = aullido()[::-1][: int(1.0 * SR)][::-1] * 0.6
    return mezclar(choque, np.concatenate([np.zeros(int(0.3 * SR)), lamento]))


# --------------------------------------------------------------------- nivel y objetos

def cruje():
    d = 0.38
    n = int(d * SR)
    t = tiempo(d)
    f = 140 * (1 + 0.3 * np.sin(2 * np.pi * 13 * t) + 0.2 * np.sin(2 * np.pi * 31 * t))
    return pasabajos(sierra(f), 1500) * adsr(n, 0.02, 0.1, 0.6, 0.12) * 0.5


def rebote():
    d = 0.38
    t = tiempo(d)
    curva = np.interp(t, [0, 0.08, 0.38], [170, 440, 300])
    return tono(vibrato(curva, 18, 0.05), d, seno, adsr(int(d * SR), 0.003, 0.1, 0.6, 0.15)) * 0.7


def engranaje():
    d = 0.22
    n = int(d * SR)
    return (pasaaltos(ruido(n, 18), 2000) * caida(n, 0.03) * 0.5
            + pulso(np.full(n, 620.0), 0.3) * caida(n, 0.05) * 0.25)


def barril():
    lienzo = np.zeros(int(0.35 * SR))
    for i, (f, s) in enumerate([(2400, 19), (1800, 20), (1200, 21)]):
        n = int(0.07 * SR)
        en(lienzo, pasabajos(ruido(n, s), f) * caida(n, 0.02), i * 0.05)
    n = int(0.15 * SR)
    en(lienzo, seno(barrido(140, 60, 0.15)) * caida(n, 0.05), 0)
    return lienzo * 0.8


def te():
    return arpegio(["C5", "E5", "G5"], 0.06, triangulo, 0.12) * 0.6


def luna():
    x = arpegio(["E6", "G#6", "B6", "E7"], 0.045, pulso, 0.1, ciclo=0.125) * 0.4
    return eco(x, 0.07, 0.4, 0.4, 0.3)


def dialogo():
    d = 0.035
    return tono(nota("A5"), d, pulso, caida(int(d * SR), 0.012), ciclo=0.25) * 0.4


def farol_encendido():
    d = 0.9
    n = int(d * SR)
    fuego = pasabajos(ruido(n, 22), barrido(300, 3000, d)) * adsr(n, 0.15, 0.2, 0.4, 0.4)
    acorde = sum(triangulo(np.full(n, nota(x))) for x in ["C4", "E4", "G4", "C5"]) * adsr(n, 0.2, 0.2, 0.6, 0.3)
    return fuego * 0.4 + acorde * 0.18


def salida():
    return eco(arpegio(["C5", "G5", "C6", "E6", "G6"], 0.07, triangulo, 0.2) * 0.5, 0.12, 0.35, 0.3, 0.5)


def menu():
    return tono(nota("E5"), 0.05, pulso, caida(int(0.05 * SR), 0.02), ciclo=0.25) * 0.5


def menu_ok():
    return arpegio(["E5", "B5"], 0.06, pulso, 0.1, ciclo=0.25) * 0.5


SONIDOS = {
    "salto": salto, "salto_doble": salto_doble, "aterrizar": aterrizar, "carga": carga,
    "carta": carta, "farol": farol, "explosion": explosion, "parry_aire": parry_aire,
    "parry": parry, "dano": dano, "derrota": derrota, "caida": caida_pozo,
    "repintado_aviso": repintado_aviso, "golpe": golpe, "tinta": tinta,
    "actor_aviso": actor_aviso, "mascara": mascara, "cuervo": cuervo,
    "agente_aviso": agente_aviso, "golpe_suelo": golpe_suelo, "bloqueo": bloqueo,
    "grunido": grunido, "embestida": embestida, "golpe_pared": golpe_pared, "zarpazo": zarpazo,
    "garra_carga": garra_carga, "garra": garra, "aullido": aullido, "transicion": transicion,
    "derrota_jefe": derrota_jefe, "cruje": cruje, "rebote": rebote, "engranaje": engranaje,
    "barril": barril, "te": te, "luna": luna, "dialogo": dialogo,
    "farol_encendido": farol_encendido, "salida": salida, "menu": menu, "menu_ok": menu_ok,
}


def main():
    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, f in SONIDOS.items():
        guardar_wav(destino / f"{nombre}.wav", f(), pico=0.85)
    print(len(SONIDOS), "sonidos en", destino)


if __name__ == "__main__":
    main()
