"""Dibuja una escena completa de game.json en una sola imagen (vista de diseño del nivel).

Compone el primer cuadro de cada instancia en su posición real (respetando el punto de
origen de cada sprite y el tamaño de los mosaicos). Sirve para revisar el nivel entero de un
vistazo, sin recorrerlo jugando.

Uso: python herramientas/vista_nivel.py juego/game.json Nivel1 salida.png
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ruta, nombre, salida = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
proyecto = json.loads(ruta.read_text(encoding="utf-8"))
raiz = ruta.parent
escena = next(l for l in proyecto["layouts"] if l["name"] == nombre)
objetos = {o["name"]: o for o in proyecto["objects"] + escena["objects"]}
vars_ = {v["name"]: v.get("value") for v in escena["variables"]}
ancho, alto = int(vars_.get("NivelAncho", 640)), int(vars_.get("NivelAlto", 360))
img = Image.new("RGBA", (ancho, alto + 40), (60, 56, 66, 255))
fondo = escena["objects"]
for o in fondo:
    if o["name"] == "FondoCiudad":
        f = Image.open(raiz / o["animations"][0]["directions"][0]["sprites"][0]["image"]).convert("RGBA")
        fx = int(vars_.get("FactorCiudadX", 0) * 1000) / 1000
        # aproximación: estirar la tira del fondo al ancho del nivel, atenuada
        f = f.resize((ancho, f.height))
        f.putalpha(110)
        img.alpha_composite(f, (0, 0))
cache = {}
def imagen(rel):
    if rel not in cache:
        cache[rel] = Image.open(raiz / rel).convert("RGBA")
    return cache[rel]
dib = ImageDraw.Draw(img)
for ins in sorted(escena["instances"], key=lambda i: i.get("zOrder", 0)):
    if ins["layer"] not in ("",):
        continue
    o = objetos.get(ins["name"])
    if not o:
        continue
    x, y = ins["x"], ins["y"]
    if o["type"] == "TiledSpriteObject::TiledSprite":
        t = imagen(o["texture"])
        w, h = int(ins.get("width") or o["width"]), int(ins.get("height") or o["height"])
        for yy in range(0, h, t.height):
            for xx in range(0, w, t.width):
                trozo = t.crop((0, 0, min(t.width, w - xx), min(t.height, h - yy)))
                img.alpha_composite(trozo, (int(x + xx), int(y + yy)))
    elif o["type"] == "Sprite":
        sp = o["animations"][0]["directions"][0]["sprites"][0]
        im = imagen(sp["image"])
        ox, oy = sp["originPoint"]["x"], sp["originPoint"]["y"]
        img.alpha_composite(im, (int(x - ox), int(y - oy)))
        if ins["name"] in ("ZonaDialogo", "Caedor"):
            dib.rectangle([x, 0 if ins["name"] == "ZonaDialogo" else y - 4, x + 3, alto], outline=(255, 200, 80, 255))
for k in range(0, ancho, 160):
    dib.text((k + 2, alto + 4), f"x{k} c{k // 16}", fill=(230, 220, 240, 255))
img.save(salida)
print(salida, img.size)
