"""Ayudantes para armar el JSON de un proyecto GDevelop 5.6 desde Python.

Sólo genera estructuras; el criterio de qué eventos y objetos tiene el juego está en
construir_juego.py. Las firmas de cada instrucción se verificaron contra los metadatos del motor
(herramientas/firma.mjs) y el resultado se valida con validar_eventos.mjs y
validar_expresiones.mjs.
"""

import re
import uuid
from pathlib import Path

from PIL import Image


def uid():
    return str(uuid.uuid4())


# ------------------------------------------------------------------ instrucciones y eventos

def C(tipo, *params, neg=False):
    """Condición."""
    return {"type": {"inverted": neg, "value": tipo}, "parameters": [str(p) for p in params]}


def A(tipo, *params):
    """Acción."""
    return {"type": {"value": tipo}, "parameters": [str(p) for p in params]}


def O(*condiciones):
    """Condición "O": alcanza con que se cumpla una de las subcondiciones."""
    return {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [],
            "subInstructions": list(condiciones)}


def E(condiciones=(), acciones=(), sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": list(condiciones),
            "actions": list(acciones), "events": list(sub)}


def PARA_CADA(objeto, condiciones=(), acciones=(), sub=()):
    return {"type": "BuiltinCommonInstructions::ForEach", "object": objeto,
            "conditions": list(condiciones), "actions": list(acciones), "events": list(sub)}


def NOTA(texto):
    """Comentario del event sheet (explica el porqué de una estructura, no el qué)."""
    return {"type": "BuiltinCommonInstructions::Comment",
            "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0},
            "comment": texto, "comment2": ""}


COLORES_GRUPO = {"jugador": (107, 63, 160), "combate": (176, 133, 214), "enemigo": (78, 110, 142),
                 "nivel": (192, 138, 58), "camara": (93, 87, 102), "hud": (138, 90, 43),
                 "jefe": (70, 39, 110)}


def GRUPO(nombre, eventos, color="jugador"):
    r, g, b = COLORES_GRUPO.get(color, (93, 87, 102))
    return {"type": "BuiltinCommonInstructions::Group", "colorR": r, "colorG": g, "colorB": b,
            "creationTime": 0, "name": nombre, "source": "", "events": list(eventos),
            "parameters": []}


def ENLACE(externo):
    return {"type": "BuiltinCommonInstructions::Link", "include": {"includeConfig": 0},
            "target": externo}


# ------------------------------------------------------------------ atajos de instrucciones

PLAT = "PlatformObject"  # se reemplaza por el nombre real del comportamiento


def anim(obj, nombre):
    return A("AnimatableCapability::AnimatableBehavior::SetName", obj, "Animation", "=", f'"{nombre}"')


def anim_es(obj, nombre, neg=False):
    return C("AnimatableCapability::AnimatableBehavior::Name", obj, "Animation", "=", f'"{nombre}"',
             neg=neg)


def anim_termino(obj, neg=False):
    return C("AnimatableCapability::AnimatableBehavior::HasAnimationEnded", obj, "Animation", neg=neg)


def voltear(obj, si):
    return A("FlippableCapability::FlippableBehavior::FlipX", obj, "Flippable", "yes" if si else "no")


def opacidad(obj, op, valor):
    return A("OpacityCapability::OpacityBehavior::SetValue", obj, "Opacity", op, valor)


def escala(obj, op, valor):
    return A("ScalableCapability::ScalableBehavior::SetValue", obj, "Scale", op, valor)


def tam(obj, w, h):
    return A("ResizableCapability::ResizableBehavior::SetSize", obj, "Resizable", w, h)


def ancho(obj, op, valor):
    return A("ResizableCapability::ResizableBehavior::SetWidth", obj, "Resizable", op, valor)


def texto(obj, valor):
    return A("TextContainerCapability::TextContainerBehavior::SetValue", obj, "Text", "=", valor)


def var_o(obj, var, op, valor):
    """Asigna/modifica una variable numérica de objeto."""
    return A("SetNumberObjectVariable", obj, var, op, valor)


def si_var_o(obj, var, op, valor, neg=False):
    return C("NumberObjectVariable", obj, var, op, valor, neg=neg)


def var_s(var, op, valor):
    """Variable numérica de escena."""
    return A("SetNumberVariable", var, op, valor)


def si_var_s(var, op, valor, neg=False):
    return C("NumberVariable", var, op, valor, neg=neg)


def texto_s(var, valor):
    return A("SetStringVariable", var, "=", valor)


def si_texto_s(var, op, valor):
    return C("StringVariable", var, op, valor)


def comparar(a, op, b, neg=False):
    return C("BuiltinCommonInstructions::CompareNumbers", a, op, b, neg=neg)


def comparar_texto(a, op, b):
    return C("BuiltinCommonInstructions::CompareStrings", a, op, b)


def una_vez():
    return C("BuiltinCommonInstructions::Once")


def al_iniciar():
    return C("SceneJustBegins", "")


def tecla(nombre, neg=False):
    return C("KeyFromTextPressed", "", f'"{nombre}"', neg=neg)


def tecla_recien(nombre):
    return C("KeyFromTextJustPressed", "", f'"{nombre}"')


def tecla_suelta(nombre):
    return C("KeyFromTextReleased", "", f'"{nombre}"')


def choca(a, b, neg=False):
    return C("CollisionNP", a, b, "", "", "", neg=neg)


def crear(obj, x, y, capa='""'):
    return A("Create", "", obj, x, y, capa)


def borrar(obj):
    return A("Delete", obj, "")


def sonido(archivo, volumen=60, tono=1):
    return A("PlaySound", "", archivo, "no", volumen, tono)


def cambiar_escena(nombre):
    return A("Scene", "", f'"{nombre}"', "yes")


# ------------------------------------------------------------------ recursos

class Recursos:
    """Registra los archivos usados por el proyecto con rutas relativas a juego/."""

    def __init__(self, raiz_juego):
        self.raiz = Path(raiz_juego)
        self.lista = []
        self._nombres = set()

    def _rel(self, ruta):
        return Path(ruta).resolve().relative_to(self.raiz.resolve()).as_posix()

    def imagen(self, ruta):
        rel = self._rel(ruta)
        if rel not in self._nombres:
            self._nombres.add(rel)
            self.lista.append({"file": rel, "kind": "image", "metadata": "", "name": rel,
                               "smoothed": False, "userAdded": True})
        return rel

    def fuente_bitmap(self, ruta):
        rel = self._rel(ruta)
        if rel not in self._nombres:
            self._nombres.add(rel)
            self.lista.append({"file": rel, "kind": "bitmapFont", "metadata": "", "name": rel,
                               "userAdded": True})
        return rel

    def audio(self, ruta, musica=False):
        rel = self._rel(ruta)
        if rel not in self._nombres:
            self._nombres.add(rel)
            self.lista.append({"file": rel, "kind": "audio", "metadata": "", "name": rel,
                               "preloadAsMusic": musica, "preloadAsSound": not musica,
                               "preloadInCache": False, "userAdded": True})
        return rel


# ------------------------------------------------------------------ objetos

def variable(nombre, valor):
    if isinstance(valor, bool):
        return {"name": nombre, "type": "boolean", "value": valor}
    if isinstance(valor, (int, float)):
        return {"name": nombre, "type": "number", "value": valor}
    if isinstance(valor, str):
        return {"name": nombre, "type": "string", "value": valor}
    if isinstance(valor, list):
        return {"name": nombre, "type": "array",
                "children": [{"type": "string", "value": v} if isinstance(v, str)
                             else {"type": "number", "value": v} for v in valor]}
    if isinstance(valor, dict):
        return {"name": nombre, "type": "structure",
                "children": [variable(k, v) for k, v in valor.items()]}
    raise TypeError(valor)


def variables(d):
    return [variable(k, v) for k, v in d.items()]


def frames_de(carpeta, prefijo):
    """Frames de una animación: archivos <prefijo>_<n>.png ordenados por n."""
    patron = re.compile(rf"^{re.escape(prefijo)}_(\d+)\.png$")
    fs = [(int(m.group(1)), f) for f in Path(carpeta).glob("*.png") if (m := patron.match(f.name))]
    return [f for _, f in sorted(fs)]


def sprite(rec, nombre, animaciones, origen, mascara=None, vars_=None, comportamientos=None,
           puntos=None, centro=None):
    """animaciones: lista de (nombre, [rutas], segundos_por_frame, en_bucle).

    centro: punto de rotación propio (por defecto el centro de la imagen). El péndulo lo
    necesita en el eje de arriba, no en el medio de la barra.
    """
    anims = []
    for (nom, rutas, t, bucle) in animaciones:
        if not rutas:
            raise ValueError(f"{nombre}.{nom}: sin frames")
        sprites = []
        for r in rutas:
            fr = {"hasCustomCollisionMask": mascara is not None, "image": rec.imagen(r),
                  "points": [{"name": n, "x": x, "y": y} for n, (x, y) in (puntos or {}).items()],
                  "originPoint": {"name": "origine", "x": origen[0], "y": origen[1]},
                  "centerPoint": ({"automatic": True, "name": "centre", "x": 0, "y": 0}
                                  if centro is None else
                                  {"automatic": False, "name": "centre", "x": centro[0],
                                   "y": centro[1]}),
                  "customCollisionMask": []}
            if mascara is not None:
                x0, y0, x1, y1 = mascara
                fr["customCollisionMask"] = [[{"x": x0, "y": y0}, {"x": x1, "y": y0},
                                              {"x": x1, "y": y1}, {"x": x0, "y": y1}]]
            sprites.append(fr)
        anims.append({"name": nom, "useMultipleDirections": False,
                      "directions": [{"looping": bucle, "timeBetweenFrames": t,
                                      "sprites": sprites}]})
    return {"adaptCollisionMaskAutomatically": False, "assetStoreId": "", "name": nombre,
            "type": "Sprite", "updateIfNotVisible": False,
            "variables": variables(vars_ or {}), "effects": [],
            "behaviors": comportamientos or [], "animations": anims}


def mosaico(rec, nombre, ruta, w, h, comportamientos=None, vars_=None):
    return {"assetStoreId": "", "name": nombre, "type": "TiledSpriteObject::TiledSprite",
            "texture": rec.imagen(ruta), "width": w, "height": h,
            "variables": variables(vars_ or {}), "effects": [], "behaviors": comportamientos or []}


def panel(rec, nombre, ruta, w, h, margen):
    return {"assetStoreId": "", "name": nombre, "type": "PanelSpriteObject::PanelSprite",
            "texture": rec.imagen(ruta), "width": w, "height": h, "tiled": False,
            "leftMargin": margen, "topMargin": margen, "rightMargin": margen,
            "bottomMargin": margen, "variables": [], "effects": [], "behaviors": []}


def texto_bitmap(rec, nombre, fuente_fnt, atlas_png, contenido, escala_=1.0, alinear="left",
                 tinte="255;255;255"):
    return {"assetStoreId": "", "name": nombre, "type": "BitmapText::BitmapTextObject",
            "variables": [], "effects": [], "behaviors": [],
            "content": {"text": contenido, "opacity": 255, "scale": escala_, "fontSize": 13,
                        "tint": tinte, "bitmapFontResourceName": rec.fuente_bitmap(fuente_fnt),
                        "textureAtlasResourceName": rec.imagen(atlas_png), "align": alinear,
                        "verticalTextAlignment": "top"}}


def plataforma(tipo="NormalPlatform"):
    return {"name": "Platform", "type": "PlatformBehavior::PlatformBehavior",
            "canBeGrabbed": False, "platformType": tipo, "yGrabOffset": 0}


def personaje_plataformas(**k):
    base = {"name": "PlatformerObject", "type": "PlatformBehavior::PlatformerObjectBehavior",
            "canGoDownFromJumpthru": True, "acceleration": 1100, "deceleration": 1500,
            "gravity": 1200, "jumpSpeed": 427, "jumpSustainTime": 0.3,
            "ladderClimbingSpeed": 150, "maxFallingSpeed": 520, "maxSpeed": 150,
            "canGrabPlatforms": False, "ignoreDefaultControls": False, "slopeMaxAngle": 60,
            "useLegacyTrajectory": False, "useRepeatedJump": False, "xGrabTolerance": 10,
            "yGrabOffset": 0}
    base.update(k)
    return base


def destruir_fuera():
    return {"name": "DestroyOutside", "type": "DestroyOutsideBehavior::DestroyOutside",
            "extraBorder": 64}


# ------------------------------------------------------------------ escenas

def capa(nombre, visible=True):
    return {"ambientLightColorB": 200, "ambientLightColorG": 200, "ambientLightColorR": 200,
            "camera3DFarPlaneDistance": 10000, "camera3DFieldOfView": 45,
            "camera3DNearPlaneDistance": 3, "cameraType": "", "followBaseLayerCamera": False,
            "isLightingLayer": False, "isLocked": False, "name": nombre, "renderingType": "",
            "visibility": visible,
            "cameras": [{"defaultSize": True, "defaultViewport": True, "height": 0,
                         "viewportBottom": 1, "viewportLeft": 0, "viewportRight": 1,
                         "viewportTop": 0, "width": 0}],
            "effects": []}


def instancia(objeto, x, y, capa_="", z=0, w=None, h=None, vars_=None, angulo=0):
    d = {"angle": angulo, "customSize": w is not None, "height": h or 0, "width": w or 0,
         "layer": capa_, "name": objeto, "persistentUuid": uid(), "x": x, "y": y, "zOrder": z,
         "numberProperties": [], "stringProperties": [],
         "initialVariables": variables(vars_ or {})}
    if w is not None:
        d["keepRatio"] = False
    return d


def escena(nombre, capas, objetos, instancias, eventos, vars_=None, color=(18, 16, 20)):
    return {"b": color[2], "disableInputWhenNotFocused": True, "mangledName": nombre,
            "name": nombre, "r": color[0], "standardSortMethod": True,
            "stopSoundsOnStartup": True, "title": "", "v": color[1],
            "uiSettings": {"grid": True, "gridType": "rectangular", "gridWidth": 16,
                           "gridHeight": 16, "gridDepth": 16, "gridOffsetX": 0, "gridOffsetY": 0,
                           "gridOffsetZ": 0, "gridColor": 10401023, "gridAlpha": 0.5,
                           "snap": True, "zoomFactor": 1.5, "windowMask": True,
                           "selectedLayer": "", "gameEditorMode": "instances-editor"},
            "objectsGroups": [], "variables": variables(vars_ or {}), "instances": instancias,
            "objects": objetos,
            "objectsFolderStructure": {"folderName": "__ROOT",
                                       "children": [{"objectName": o["name"]} for o in objetos]},
            "events": eventos, "layers": capas, "behaviorsSharedData": []}


def externo(nombre, escena_asociada, eventos):
    return {"associatedLayout": escena_asociada, "lastChangeTimeStamp": 0, "name": nombre,
            "events": eventos}


def tamano(ruta):
    with Image.open(ruta) as im:
        return im.size
