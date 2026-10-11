"""Bloques básicos de síntesis para el audio de Toonaria (efectos y música).

Todo el audio del juego se genera por código con las mismas herramientas que usaban las
consolas de 8 y 16 bits: ondas cuadradas de distinto ancho de pulso, triangulares, diente de
sierra y ruido, con envolventes de volumen y de altura. Se eligió así por coherencia con el
pixel art (sonido "chiptune" para imagen de baja resolución) y porque cada sonido queda
documentado como una receta que se puede ajustar y volver a generar.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter

SR = 32000  # frecuencia de muestreo: alcanza de sobra para ondas de consola retro


def tiempo(dur):
    return np.arange(int(dur * SR)) / SR


def nota(nombre):
    """'A4' -> 440 Hz. Admite sostenidos (C#4) y bemoles (Bb3)."""
    letras = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    semis = letras[nombre[0]]
    resto = nombre[1:]
    while resto and resto[0] in "#b":
        semis += 1 if resto[0] == "#" else -1
        resto = resto[1:]
    octava = int(resto)
    return 440.0 * 2 ** ((semis + 12 * (octava - 4)) / 12)


def fase(frecuencia):
    """Integra una frecuencia (constante o curva) para obtener la fase en ciclos."""
    f = np.broadcast_to(np.asarray(frecuencia, dtype=np.float64), np.shape(frecuencia))
    return np.cumsum(f) / SR


def pulso(frec, ciclo=0.5):
    """Onda cuadrada con ancho de pulso: 0.5 suena hueca, 0.125 suena nasal (la "voz" NES)."""
    return np.where((fase(frec) % 1.0) < ciclo, 1.0, -1.0)


def triangulo(frec):
    p = fase(frec) % 1.0
    return 4 * np.abs(p - 0.5) - 1


def sierra(frec):
    return 2 * (fase(frec) % 1.0) - 1


def seno(frec):
    return np.sin(2 * np.pi * fase(frec))


def ruido(n, semilla=0, periodo=1):
    """Ruido blanco; con periodo > 1 cada valor se repite (ruido "granulado" más grave)."""
    rnd = np.random.default_rng(semilla)
    base = rnd.uniform(-1, 1, n // periodo + 1)
    return np.repeat(base, periodo)[:n]


def barrido(f0, f1, dur, curva="exp"):
    t = np.linspace(0, 1, int(dur * SR), endpoint=False)
    if curva == "exp":
        return f0 * (f1 / f0) ** t
    return f0 + (f1 - f0) * t


def vibrato(frec, vel=6.0, prof=0.02, retardo=0.0):
    """Modula la frecuencia; el retardo deja la nota limpia al principio, como un cantante."""
    frec = np.asarray(frec, dtype=np.float64)
    t = np.arange(frec.size) / SR
    entrada = np.clip((t - retardo) / 0.08, 0, 1)
    return frec * (1 + prof * entrada * np.sin(2 * np.pi * vel * t))


def adsr(n, a=0.005, d=0.05, s=0.6, r=0.05, sostenido=None):
    """Envolvente de volumen. `sostenido` (en s) es cuánto dura la nota antes de soltarla."""
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    sos_n = n - a_n - d_n - r_n if sostenido is None else int(sostenido * SR) - a_n - d_n
    sos_n = max(sos_n, 0)
    env = np.concatenate([np.linspace(0, 1, a_n, endpoint=False),
                          np.linspace(1, s, d_n, endpoint=False),
                          np.full(sos_n, s),
                          np.linspace(s, 0, r_n)])
    if env.size < n:
        env = np.concatenate([env, np.zeros(n - env.size)])
    return env[:n]


def caida(n, tau=0.1):
    """Decaimiento exponencial (golpes, campanas)."""
    return np.exp(-np.arange(n) / SR / tau)


def pasabajos(x, corte):
    """Filtro de un polo: suaviza el sonido. `corte` puede ser constante o una curva."""
    corte = np.broadcast_to(np.asarray(corte, dtype=np.float64), x.shape)
    k = 1 - np.exp(-2 * np.pi * corte / SR)
    if np.all(k == k.flat[0]):
        return lfilter([k.flat[0]], [1, k.flat[0] - 1], x)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(x.size):
        acc += k[i] * (x[i] - acc)
        y[i] = acc
    return y


def pasaaltos(x, corte):
    return x - pasabajos(x, corte)


def eco(x, retardo=0.18, realimentacion=0.35, mezcla=0.3, cola=1.0):
    """Eco simple: copias atrasadas y más bajas. Agrega cola al final del sonido."""
    d = int(retardo * SR)
    salida = np.concatenate([x, np.zeros(int(cola * SR))])
    mojado = np.zeros_like(salida)
    # Suma de copias corridas k * retardo con volumen realimentacion^(k-1), hasta que la
    # copia ya no se oye (equivale a la realimentación, sin recorrer muestra por muestra).
    k, amp = 1, 1.0
    while amp > 0.01 and k * d < salida.size:
        mojado[k * d:] += amp * salida[:salida.size - k * d]
        k, amp = k + 1, amp * realimentacion
    return salida + mezcla * mojado


def mezclar(*partes):
    n = max(p.size for p in partes)
    out = np.zeros(n)
    for p in partes:
        out[:p.size] += p
    return out


def en(lienzo, sonido, inicio):
    """Suma `sonido` dentro de `lienzo` a partir del segundo `inicio` (recorta lo que sobra)."""
    i = int(inicio * SR)
    if i >= lienzo.size:
        return lienzo
    j = min(lienzo.size, i + sonido.size)
    lienzo[i:j] += sonido[:j - i]
    return lienzo


def normalizar(x, pico=0.9):
    m = np.max(np.abs(x))
    return x if m == 0 else x * (pico / m)


def guardar_wav(ruta, x, pico=0.9):
    x = normalizar(x, pico)
    # Fundido de 3 ms en los bordes: evita el "clic" de cortar una onda en la mitad.
    f = min(int(0.003 * SR), x.size // 2)
    if f:
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
    wavfile.write(str(ruta), SR, (x * 32767).astype(np.int16))
