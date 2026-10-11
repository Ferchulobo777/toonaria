"""Música de Toonaria: un secuenciador mínimo (estilo tracker) y los temas del juego.

Cada tema se escribe como pistas de texto, un token por paso:
    "A4" empieza una nota · "." la sostiene · "-" silencio · "x" golpe (percusión)
Los acompañamientos (bajo, acordes, arpegios) se arman a partir del cifrado de acordes, así
la armonía está escrita una sola vez y la melodía se apoya en ella.

Decisiones de composición (cada barrio tiene su propio carácter, igual que su paleta):
- Título y final: vals en Re menor con caja de música. La caja de música es un objeto de la
  carpa de Ambrosio, el recuerdo que mueve toda la historia.
- Prólogo (la carpa, de día): Fa mayor en 6/8 con acordeón. Es el único tema en modo mayor:
  es el pasado feliz antes de la luna.
- Barrios (niveles 1 y 2): La menor con el sol sostenido de la escala armónica, bajo saltarín
  y caja en el contratiempo: "dibujo animado de terror", más travieso que amenazante.
- Corazón (nivel 3): Mi menor con el acorde napolitano (Fa mayor): más tenso, campana de reloj.
- Jefe: Mi menor a 160 pulsos con bajo constante en corcheas y la misma segunda menor (Fa)
  insistiendo: la sensación de que algo se descompone.
- Los temas que se repiten están pensados para hacer bucle sin corte: el último compás vuelve
  al acorde del primero y la cola del eco se suma al comienzo.

Uso: python musica.py <carpeta_salida>   (genera .ogg con ffmpeg)
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

from sintesis import (SR, adsr, barrido, caida, guardar_wav, nota, pasaaltos, pasabajos, pulso,
                      ruido, seno, sierra, triangulo, vibrato)

# --------------------------------------------------------------------- instrumentos


def inst_caja_musical(f, d):
    n = int((d + 0.9) * SR)
    base = np.full(n, f)
    x = triangulo(base) * 0.7 + seno(base * 2) * 0.25 + seno(base * 3.01) * 0.08
    return x * caida(n, 0.45) * adsr(n, 0.002, 0.01, 1, 0.05)


def inst_acordeon(f, d):
    n = int((d + 0.1) * SR)
    t = np.arange(n) / SR
    a = pulso(vibrato(np.full(n, f), 5.2, 0.004), 0.5)
    b = pulso(np.full(n, f * 1.004), 0.25)
    tremolo = 0.85 + 0.15 * np.sin(2 * np.pi * 5.5 * t)
    return pasabajos((a * 0.6 + b * 0.4) * tremolo, 2600) * adsr(n, 0.03, 0.05, 0.8, 0.08, sostenido=d)


def inst_lead(f, d):
    n = int((d + 0.08) * SR)
    x = pulso(vibrato(np.full(n, f), 5.5, 0.012, 0.15), 0.25)
    return x * adsr(n, 0.004, 0.08, 0.7, 0.06, sostenido=d)


def inst_lead_suave(f, d):
    n = int((d + 0.12) * SR)
    x = pulso(vibrato(np.full(n, f), 5, 0.015, 0.2), 0.5)
    return pasabajos(x, 2200) * adsr(n, 0.015, 0.1, 0.75, 0.1, sostenido=d)


def inst_bajo(f, d):
    n = int((d + 0.05) * SR)
    return triangulo(np.full(n, f)) * adsr(n, 0.004, 0.05, 0.85, 0.04, sostenido=d)


def inst_bajo_pulso(f, d):
    n = int((d + 0.04) * SR)
    return pasabajos(pulso(np.full(n, f), 0.5), 700) * adsr(n, 0.003, 0.06, 0.7, 0.03, sostenido=d)


def inst_acorde(f, d):
    n = int((d + 0.06) * SR)
    return pulso(np.full(n, f), 0.25) * adsr(n, 0.003, 0.04, 0.4, 0.05, sostenido=d)


def inst_arpegio(f, d):
    n = int((d + 0.05) * SR)
    return pulso(np.full(n, f), 0.125) * caida(n, 0.09)


def inst_pad(f, d):
    n = int((d + 0.4) * SR)
    x = sum(sierra(np.full(n, f * k)) for k in (0.997, 1.0, 1.003)) / 3
    return pasabajos(x, 1100) * adsr(n, 0.25, 0.2, 0.8, 0.4, sostenido=d)


def inst_campana(f, d):
    n = int(2.0 * SR)
    base = np.full(n, f)
    return (seno(base) + 0.5 * seno(base * 2.76) + 0.25 * seno(base * 5.4)) * caida(n, 0.6)


def inst_bombo(f, d):
    n = int(0.18 * SR)
    return seno(barrido(130, 42, 0.18)) * caida(n, 0.07)


def inst_caja(f, d):
    n = int(0.16 * SR)
    return (pasaaltos(ruido(n, 31), 1200) * caida(n, 0.05) * 0.8
            + triangulo(barrido(220, 160, 0.16)) * caida(n, 0.04) * 0.5)


def inst_platillo(f, d):
    n = int(0.06 * SR)
    return pasaaltos(ruido(n, 32), 6000) * caida(n, 0.018)


def inst_tom(f, d):
    n = int(0.25 * SR)
    return seno(barrido(210, 85, 0.25)) * caida(n, 0.09)


INSTRUMENTOS = {
    "caja_musical": inst_caja_musical, "acordeon": inst_acordeon, "lead": inst_lead,
    "lead_suave": inst_lead_suave, "bajo": inst_bajo, "bajo_pulso": inst_bajo_pulso,
    "acorde": inst_acorde, "arpegio": inst_arpegio, "pad": inst_pad, "campana": inst_campana,
    "bombo": inst_bombo, "caja": inst_caja, "platillo": inst_platillo, "tom": inst_tom,
}

# --------------------------------------------------------------------- armonía

ACORDES = {"m": [0, 3, 7], "": [0, 4, 7], "7": [0, 4, 7, 10], "dim": [0, 3, 6]}


def raiz_y_tipo(cifra):
    raiz = cifra[0] + (cifra[1] if len(cifra) > 1 and cifra[1] in "#b" else "")
    return raiz, cifra[len(raiz):]


def notas_acorde(cifra, octava):
    raiz, tipo = raiz_y_tipo(cifra)
    base = nota(f"{raiz}{octava}")
    return [base * 2 ** (s / 12) for s in ACORDES[tipo]]


def pista_desde_acordes(acordes, pasos_compas, patron, octava, dur=1):
    """patron: lista de (paso_en_el_compás, índice_de_nota_del_acorde). Índices >= len suben
    de octava; "r" es la raíz una octava arriba. Devuelve notas (paso, duración, frecuencia)."""
    notas = []
    for c, cifra in enumerate(acordes):
        tonos = notas_acorde(cifra, octava)
        for paso, idx in patron:
            if idx == "r":
                f = tonos[0] * 2
            else:
                f = tonos[idx % len(tonos)] * 2 ** (idx // len(tonos))
            notas.append((c * pasos_compas + paso, dur, f))
    return notas


def pista_texto(texto):
    """Convierte "A4 . . - C5 ." en notas (paso, duración, frecuencia) o golpes (frecuencia 0)."""
    tokens = texto.split()
    notas, actual = [], None
    for i, tk in enumerate(tokens):
        if tk == ".":
            if actual is not None:
                actual[1] += 1
            continue
        if actual is not None:
            notas.append(tuple(actual))
            actual = None
        if tk == "-":
            continue
        actual = [i, 1, 0.0 if tk == "x" else nota(tk)]
    if actual is not None:
        notas.append(tuple(actual))
    return notas, len(tokens)


def percusion(patron_compas, compases):
    return pista_texto(" ".join([patron_compas] * compases))[0]


# --------------------------------------------------------------------- render


def render(tema):
    total = tema["compases"] * tema["pasos_compas"]
    for inst, notas, _ in tema["pistas"]:
        fuera = [p for (p, _, _) in notas if p >= total]
        if fuera:
            raise ValueError(f"{inst}: notas fuera del tema (paso {fuera[0]} de {total})")
    paso = 60.0 / tema["bpm"] / tema["pasos_por_pulso"]
    largo = tema["compases"] * tema["pasos_compas"] * paso
    n = int(largo * SR)
    mezcla = np.zeros(n + int(3.0 * SR))
    for inst, notas, vol in tema["pistas"]:
        sintetizar = INSTRUMENTOS[inst]
        for (p, dur, f) in notas:
            sonido = sintetizar(f, dur * paso * 0.97) * vol
            i = int(p * paso * SR)
            j = min(mezcla.size, i + sonido.size)
            mezcla[i:j] += sonido[:j - i]
    # Bucle sin corte: lo que suena después del final (colas de eco y de las notas largas)
    # se suma al principio, que es donde el bucle lo va a hacer sonar.
    cola = mezcla[n:]
    mezcla = mezcla[:n]
    mezcla[:cola.size] += cola[:n]
    return mezcla


def tema_titulo(bpm=92, final=False):
    acordes = ["Dm", "Dm", "Bb", "Bb", "Gm", "A", "Dm", "A",
               "Dm", "F", "Bb", "Gm", "Gm", "A", "Dm", "A"]
    melodia = """
        A4 . . . D5 .   F5 . E5 . D5 .   F5 . . . D5 .   Bb4 . C5 . D5 .
        G5 . F5 . E5 .  C#5 . . . E5 .   D5 . F5 . A5 .   G5 . . . E5 .
        A5 . . . D6 .   C6 . A5 . F5 .   D6 . . . Bb5 .   G5 . Bb5 . D6 .
        C6 . Bb5 . G5 . A5 . C#6 . E6 .  D6 . . . . .     C#5 . E5 . A4 .
    """
    mel, _ = pista_texto(melodia)
    bajo = pista_desde_acordes(acordes, 6, [(0, 0)], 2, dur=2)
    acomp = (pista_desde_acordes(acordes, 6, [(2, 1), (4, 1)], 4)
             + pista_desde_acordes(acordes, 6, [(2, 2), (4, 2)], 4))
    pad = pista_desde_acordes(acordes, 6, [(0, 0), (0, 1), (0, 2)], 3, dur=6)
    pistas = [("caja_musical", mel, 0.5), ("pad", pad, 0.09)]
    if not final:
        pistas += [("bajo", bajo, 0.32), ("acorde", acomp, 0.06)]
    return {"bpm": bpm, "pasos_por_pulso": 2, "pasos_compas": 6, "compases": 16, "pistas": pistas}


def tema_carpa():
    acordes = ["F", "C", "Dm", "Bb", "F", "C", "Bb", "F",
               "Bb", "F", "Gm", "C", "F", "Dm", "Gm", "F"]
    melodia = """
        C5 . A4 F4 . A4   G4 . E4 C4 . E4   F4 . A4 D5 . C5   Bb4 . . D5 . .
        A4 . C5 F5 . E5   D5 . C5 Bb4 . G4  A4 . Bb4 G4 . E4  F4 . . . . -
        D5 . F5 D5 . Bb4  C5 . A4 F4 . A4   Bb4 . D5 G5 . F5  E5 . . C5 . .
        A5 . G5 F5 . C5   D5 . F5 A5 . F5   G5 . F5 E5 . C5   F5 . . . . -
    """
    mel, _ = pista_texto(melodia)
    bajo = pista_desde_acordes(acordes, 6, [(0, 0), (3, 2)], 2, dur=2)
    acomp = (pista_desde_acordes(acordes, 6, [(1, 1), (4, 1)], 4)
             + pista_desde_acordes(acordes, 6, [(1, 2), (4, 2)], 4))
    return {"bpm": 70, "pasos_por_pulso": 3, "pasos_compas": 6, "compases": 16,
            "pistas": [("acordeon", mel, 0.32), ("bajo", bajo, 0.36), ("acorde", acomp, 0.07),
                       ("caja_musical", pista_desde_acordes(acordes[::2], 12, [(0, 2)], 5), 0.12)]}


def tema_barrios():
    acordes = ["Am", "Am", "F", "E", "Am", "Am", "Dm", "E",
               "F", "G", "Em", "Am", "F", "G", "E", "E"]
    melodia = """
        A4 - C5 - E5 . D5 C5     B4 . A4 - G#4 . A4 -     F4 - A4 - C5 . B4 A4     G#4 . . . B4 . E4 -
        A4 - C5 - E5 . A5 .      G5 . E5 - C5 . A4 -      D5 . F5 . A5 . G5 F5     E5 . . . G#4 . B4 .
        C5 . . A4 F4 - A4 -      B4 . . G4 D4 - G4 -      E5 . D5 . B4 . G4 .      A4 . . . . . - -
        F5 . E5 . C5 . A4 .      D5 . C5 . B4 . G4 .      G#4 . B4 . E5 . G#5 .    B5 . . . E5 . - -
    """
    mel, _ = pista_texto(melodia)
    bajo = pista_desde_acordes(acordes, 8, [(0, 0), (2, 3), (4, 2), (6, 3)], 2)
    arp = pista_desde_acordes(acordes, 8, [(i, i % 3) for i in range(8)], 5)
    return {"bpm": 128, "pasos_por_pulso": 2, "pasos_compas": 8, "compases": 16,
            "pistas": [("lead", mel, 0.24), ("bajo_pulso", bajo, 0.42), ("arpegio", arp, 0.06),
                       ("bombo", percusion("x - - - x - - -", 16), 0.5),
                       ("caja", percusion("- - x - - - x -", 16), 0.22),
                       ("platillo", percusion("x x x x x x x x", 16), 0.06)]}


def tema_corazon():
    acordes = ["Em", "C", "Am", "B7", "Em", "C", "F", "B7",
               "Em", "D", "C", "B7", "Am", "C", "B7", "B7"]
    melodia = """
        E5 . . . G5 . F#5 E5     E5 . D5 . C5 . . .       A4 . C5 . E5 . D5 C5     B4 . . . D#5 . F#5 .
        G5 . . . F#5 . E5 .      E5 . G5 . C6 . B5 A5     A5 . . . F5 . C5 .       B4 . D#5 . F#5 . A5 .
        G5 . . . E5 . B4 .       A5 . . . F#5 . D5 .      G5 . . . E5 . C5 .       F#5 . . . D#5 . B4 .
        C6 . B5 . A5 . E5 .      G5 . F#5 . E5 . C5 .     D#5 . F#5 . B5 . A5 .    F#5 . . . D#5 . B4 .
    """
    mel, _ = pista_texto(melodia)
    bajo = pista_desde_acordes(acordes, 8, [(i, 3 if i in (3, 7) else 0) for i in range(8)], 2)
    campana = pista_desde_acordes(acordes[::2], 16, [(0, 0)], 5)
    return {"bpm": 138, "pasos_por_pulso": 2, "pasos_compas": 8, "compases": 16,
            "pistas": [("lead_suave", mel, 0.26), ("bajo_pulso", bajo, 0.38),
                       ("pad", pista_desde_acordes(acordes, 8, [(0, 0), (0, 1), (0, 2)], 3, dur=8), 0.08),
                       ("campana", campana, 0.13),
                       ("bombo", percusion("x - - x x - - -", 16), 0.5),
                       ("caja", percusion("- - x - - - x -", 16), 0.22),
                       ("platillo", percusion("x - x - x - x -", 16), 0.06)]}


def tema_jefe():
    acordes = ["Em", "F", "Em", "F", "Em", "D", "C", "B7",
               "Am", "B7", "Em", "C", "Am", "F", "B7", "B7"]
    melodia = """
        E5 . . . B4 . E5 .       F5 . . . E5 . D5 .       E5 . G5 . B5 . A5 G5     F5 . . . . . E5 .
        B5 . . . G5 . E5 .       F#5 . . . A5 . D6 .      E6 . . . C6 . G5 .       F#5 . D#5 . B4 . D#5 .
        C6 . . . B5 . A5 .       B5 . . . A5 . F#5 .      G5 . . . E5 . B4 .       C5 . E5 . G5 . C6 .
        E6 . . . C6 . A5 .       F5 . A5 . C6 . A5 .      B5 . . . D#6 . F#6 .     F#6 . . . D#6 . B5 .
    """
    mel, _ = pista_texto(melodia)
    bajo = pista_desde_acordes(acordes, 8, [(0, 0), (1, 0), (2, "r"), (3, 0), (4, 0), (5, "r"), (6, 0), (7, "r")], 2)
    arp = pista_desde_acordes(acordes, 8, [(i, [0, 1, 2, 3][i % 4]) for i in range(8)], 4)
    redoble = " ".join(["- - x - - - x -"] * 7 + ["- - x - x x x x"])
    return {"bpm": 160, "pasos_por_pulso": 2, "pasos_compas": 8, "compases": 16,
            "pistas": [("lead", mel, 0.25), ("bajo_pulso", bajo, 0.4), ("arpegio", arp, 0.07),
                       ("bombo", percusion("x - x - x - x -", 16), 0.48),
                       ("caja", pista_texto(redoble + " " + redoble)[0], 0.24),
                       ("platillo", percusion("x x x x x x x x", 16), 0.06),
                       ("tom", percusion("- - - - - - - -  - - - - - - - -  - - - - - - - -  - - - - - x x x", 4), 0.3)]}


def con_variacion(tema, timbre="lead_suave", octava=-1, arpegio=1.8):
    """Duplica el tema: la segunda vuelta cambia el timbre de la melodía y la corre de octava,
    y sube el arpegio. Un nivel dura varios minutos; un bucle de 30 s idéntico cansa, uno de
    60 s con dos caras distintas se escucha como una canción."""
    total = tema["compases"] * tema["pasos_compas"]
    pistas = list(tema["pistas"])
    melodia = tema["pistas"][0]
    for inst, notas, vol in tema["pistas"]:
        if (inst, notas, vol) is melodia:
            pistas.append((timbre, [(p + total, d, f * 2 ** octava) for p, d, f in notas], vol * 1.1))
        elif inst == "arpegio":
            pistas.append((inst, [(p + total, d, f) for p, d, f in notas], vol * arpegio))
        else:
            pistas.append((inst, [(p + total, d, f) for p, d, f in notas], vol))
    return dict(tema, compases=tema["compases"] * 2, pistas=pistas)


TEMAS = {
    "titulo": tema_titulo(), "carpa": con_variacion(tema_carpa(), "caja_musical", 1),
    "barrios": con_variacion(tema_barrios()), "corazon": con_variacion(tema_corazon(), "lead", 0),
    "jefe": con_variacion(tema_jefe(), "lead_suave", 0, 2.2),
    "final": tema_titulo(bpm=72, final=True),
}


def main():
    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    elegidos = sys.argv[2:] or list(TEMAS)
    with tempfile.TemporaryDirectory() as tmp:
        for nombre in elegidos:
            audio = render(TEMAS[nombre])
            wav = Path(tmp) / f"{nombre}.wav"
            guardar_wav(wav, audio, pico=0.8)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libvorbis",
                            "-q:a", "4", str(destino / f"{nombre}.ogg")], check=True)
            print(nombre, f"{audio.size / SR:.1f} s")


if __name__ == "__main__":
    main()
