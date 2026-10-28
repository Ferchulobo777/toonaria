"""Arma el pitch en video de Toonaria (1280 × 720, 30 cuadros por segundo) con clips del juego.

El guion del pitch sigue la estructura que pide la cátedra: gancho, historia, mecánicas, mundo y
cierre. Las tomas se graban con `probar_juego.mjs` (pasos `lento` y `grabarInicio`) y acá se
combinan con placas de texto, leyendas y la música del propio juego.

Los cuadros se generan en memoria y van directo a ffmpeg por una tubería: no se escriben miles de
imágenes intermedias a disco.

Uso: python herramientas/armar_pitch.py <carpeta_clips> <salida.mp4>
     (cada clip es una subcarpeta con cuadros g_0000.jpg, g_0001.jpg, ...)
"""

import itertools
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
W, H, FPS = 1280, 720, 30
FUENTES = Path("C:/Windows/Fonts")
TITULAR = ImageFont.truetype(str(FUENTES / "georgiab.ttf"), 54)
TITULAR_CHICO = ImageFont.truetype(str(FUENTES / "georgiab.ttf"), 38)
LEYENDA = ImageFont.truetype(str(FUENTES / "segoeuib.ttf"), 30)
LEYENDA_TEXTO = ImageFont.truetype(str(FUENTES / "segoeui.ttf"), 30)
CHICA = ImageFont.truetype(str(FUENTES / "segoeui.ttf"), 26)

TINTA = (18, 16, 20)
LUNA = (238, 226, 246)
MORADO = (176, 133, 214)
AMBAR = (246, 199, 96)

# Guion: (tipo, datos, segundos, tema musical).
# placa: líneas de texto centradas. clip: (carpeta, cuadro inicial, palabra clave, leyenda).
GUION = [
    ("placa", ["Una ciudad de tinta."], 2.6, "titulo"),
    ("clip", ("titulo", 20, "", ""), 3.4, "titulo"),
    ("placa", ["En Toonaria, la luna llena", "repinta a su gente."], 3.2, "titulo"),
    ("clip", ("prologo", 0, "EL PRÓLOGO", "Ambrosio, el farolero, le enseña a pelear a Ventura."), 6.0, "titulo"),
    ("placa", ["Una noche, Ambrosio", "miró la luna de más."], 3.0, "titulo"),
    ("clip", ("nivel1", 30, "TRES BARRIOS", "Ventura cruza la ciudad para encontrarlo."), 6.0, "barrios"),
    ("clip", ("carga", 0, "CARGÁ", "cuanto más aguantás, más fuerte. La carta completa explota."), 4.4, "barrios"),
    ("clip", ("parry", 0, "DEVOLVÉ", "el parry le regresa a cada enemigo lo que te tira."), 6.0, "barrios"),
    ("clip", ("pendulos", 20, "SALTÁ", "péndulos, toldos, tablones y nubes de tinta."), 6.0, "barrios"),
    ("clip", ("nivel3", 40, "LEÉ AL ENEMIGO", "cuatro enemigos, y cada uno avisa antes de atacar."), 6.0, "barrios"),
    ("placa", ["En la cima de la torre,", "te espera él."], 2.8, "jefe"),
    ("clip", ("jefe", 20, "EL JEFE", "dos fases con ciclos que se aprenden."), 7.0, "jefe"),
    ("clip", ("resultados", 10, "SUPERATE", "puntaje y rango al final de cada nivel."), 3.6, "jefe"),
    ("final", None, 4.6, "final"),
    ("creditos", None, 4.4, "final"),
]


def fondo_placa():
    """Negro tinta con un halo morado tenue: el mismo clima que la luna detrás del título."""
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W * 0.55)) ** 2 + ((y - H * 0.45) / (H * 0.6)) ** 2)
    halo = np.clip(1 - d, 0, 1)[..., None] ** 1.6
    base = np.array(TINTA, float) + halo * (np.array((70, 39, 110), float) - np.array(TINTA, float))
    return Image.fromarray(base.astype(np.uint8))


FONDO = fondo_placa()
LOGO = Image.open(RAIZ / "juego" / "assets" / "pixel" / "titulo" / "logo.png").convert("RGBA")
LOGO = LOGO.resize((LOGO.width * 2, LOGO.height * 2), Image.NEAREST)


def texto_centrado(img, lineas, fuente, y0, color, sep=14):
    dib = ImageDraw.Draw(img)
    alturas = [dib.textbbox((0, 0), l, font=fuente)[3] for l in lineas]
    y = y0 - (sum(alturas) + sep * (len(lineas) - 1)) / 2
    for l, h in zip(lineas, alturas):
        ancho = dib.textlength(l, font=fuente)
        dib.text(((W - ancho) / 2, y), l, font=fuente, fill=color)
        y += h + sep


def placa(lineas):
    img = FONDO.copy()
    texto_centrado(img, lineas, TITULAR, H * 0.47, LUNA)
    return img


def placa_final():
    img = FONDO.copy()
    img.paste(LOGO, ((W - LOGO.width) // 2, 150), LOGO)
    texto_centrado(img, ["Prólogo · tres niveles · jefe final"], TITULAR_CHICO, 430, LUNA)
    texto_centrado(img, ["Se juega en el navegador, en PC y en el celular"], LEYENDA_TEXTO, 500, MORADO)
    texto_centrado(img, ["Jugalo en itch.io"], LEYENDA, 570, AMBAR)
    return img


def placa_creditos():
    img = FONDO.copy()
    texto_centrado(img, ["Un juego del Grupo 11"], TITULAR_CHICO, 210, AMBAR)
    texto_centrado(img, ["Fernando Rodríguez", "Mateo Fernández", "Natalia Ailén González",
                         "Fernando Rubén Bareiro Ruiz"], LEYENDA_TEXTO, 360, LUNA, sep=10)
    texto_centrado(img, ["Multimedia y Juegos en Web · Tecnicatura Universitaria en Desarrollo Web",
                         "FCAD · Universidad Nacional de Entre Ríos · 2026"], CHICA, 560, MORADO, sep=8)
    return img


def leyenda(img, clave, texto, arriba=False):
    """Franja semitransparente con la palabra clave resaltada. Va abajo, salvo en las tomas
    donde abajo está la caja de diálogo del juego."""
    if not texto:
        return img
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dib = ImageDraw.Draw(capa)
    y0 = 100 if arriba else H - 96
    dib.rectangle((0, y0, W, y0 + 68), fill=(18, 16, 20, 200))
    x = 48
    if clave:
        dib.text((x, y0 + 14), clave, font=LEYENDA, fill=AMBAR)
        x += dib.textlength(clave, font=LEYENDA) + 16
    dib.text((x, y0 + 14), texto, font=LEYENDA_TEXTO, fill=LUNA)
    return Image.alpha_composite(img.convert("RGBA"), capa).convert("RGB")


def cuadros_clip(carpeta, inicio, n):
    fs = sorted(carpeta.glob("g_*.jpg"))[inicio:]
    if not fs:
        raise SystemExit(f"sin cuadros en {carpeta}")
    for i in range(n):
        f = fs[min(i, len(fs) - 1)]
        yield Image.open(f).convert("RGB").resize((W, H), Image.NEAREST)


def fundido(img, t, dur, entrada=0.35, salida=0.35):
    """Fundido desde y hacia negro en los bordes de cada segmento."""
    k = min(1.0, t / entrada if entrada else 1.0, (dur - t) / salida if salida else 1.0)
    if k >= 1:
        return img
    return Image.blend(Image.new("RGB", (W, H), TINTA), img, max(0.0, k))


def musica(salida_wav, tramos):
    """Encadena los temas del juego según el guion, con fundidos entre uno y otro."""
    entradas, filtros, pos = [], [], {}
    for tema, _ in tramos:
        if tema not in pos:
            pos[tema] = len(pos)
            entradas += ["-i", str(RAIZ / "juego" / "assets" / "musica" / f"{tema}.ogg")]
    inicio_tema, partes = {}, []
    for k, (tema, dur) in enumerate(tramos):
        desde = inicio_tema.get(tema, 0.0)
        inicio_tema[tema] = desde + dur
        filtros.append(f"[{pos[tema]}:a]atrim={desde:.3f}:{desde + dur:.3f},asetpts=PTS-STARTPTS,"
                       f"afade=t=in:d=0.6,afade=t=out:st={max(0, dur - 0.8):.3f}:d=0.8[a{k}]")
        partes.append(f"[a{k}]")
    filtros.append("".join(partes) + f"concat=n={len(partes)}:v=0:a=1[m]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *entradas, "-filter_complex",
                    ";".join(filtros), "-map", "[m]", "-ac", "2", str(salida_wav)], check=True)


def main():
    clips, salida = Path(sys.argv[1]), Path(sys.argv[2])
    # La música cambia de tema por bloques consecutivos, no en cada segmento.
    tramos = []
    for tipo, datos, dur, tema in GUION:
        if tramos and tramos[-1][0] == tema:
            tramos[-1][1] += dur
        else:
            tramos.append([tema, dur])
    audio = salida.with_suffix(".wav")
    musica(audio, tramos)
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", str(audio), "-c:v", "libx264", "-preset", "slow",
         "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
         "-movflags", "+faststart", str(salida)], stdin=subprocess.PIPE)
    total = 0
    for tipo, datos, dur, _ in GUION:
        n = round(dur * FPS)
        if tipo == "clip":
            carpeta, inicio, clave, texto = datos
            fuente = cuadros_clip(clips / carpeta, inicio, n)
        else:
            fija = {"placa": lambda: placa(datos), "final": placa_final,
                    "creditos": placa_creditos}[tipo]()
            fuente = itertools.repeat(fija, n)
        for i, cuadro in enumerate(fuente):
            if tipo == "clip":
                cuadro = leyenda(cuadro, clave, texto, arriba=carpeta == "prologo")
            ffmpeg.stdin.write(fundido(cuadro, i / FPS, dur).tobytes())
        total += n
    ffmpeg.stdin.close()
    ffmpeg.wait()
    audio.unlink(missing_ok=True)
    print(f"pitch {salida} {total / FPS:.1f} s")


if __name__ == "__main__":
    main()
