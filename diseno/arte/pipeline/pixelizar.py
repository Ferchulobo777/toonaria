"""Convierte una hoja de animación ilustrada "estilo pixel" en frames de pixel art real.

Las hojas ilustradas "estilo pixel" imitan el pixel art pero no respetan una grilla exacta: cada
"píxel" mide distinto, hay bordes suavizados y aparecen colores fuera de paleta. Para que todos
los sprites del juego compartan la misma grilla y la misma paleta, cada hoja pasa por este
proceso:

1. Se recorta el fondo de croma (verde puro) y cada figura se asigna a su celda de la grilla.
2. Se fija una escala común para toda la hoja a partir de una pose de pie de referencia, de modo
   que el personaje no cambie de tamaño al pasar de una animación a otra.
3. Cada píxel de salida toma el color predominante de su bloque en la imagen original
   (cuantizado a la paleta cerrada en espacio Lab, que se acerca más a la percepción humana que
   RGB). El contorno de tinta tiene prioridad aunque no sea mayoría, porque si se pierde un
   píxel de contorno la silueta deja de leerse a tamaño real.
4. La fase de la grilla se ajusta por frame buscando la alineación con bloques más "puros", que
   es la que mejor coincide con la grilla con la que se dibujó la hoja.
5. Todos los frames se ubican en un lienzo fijo con un ancla común (cabeza o pies), así el
   personaje no "tiembla" al reproducir la animación en el motor.

Uso típico:
    python pixelizar.py hoja.png salida/ --nombre ventura_correr --columnas 4 --filas 2
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from paleta import INDICE_TINTA, NOMBRES, PALETA_RGB

TRANSPARENTE = -1


def rgb_a_lab(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124, 0.3576, 0.1805],
                  [0.2126, 0.7152, 0.0722],
                  [0.0193, 0.1192, 0.9505]])
    xyz = (c @ m.T) / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16,
                     500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], -1)


def mascara_fondo(rgb, tipo="auto"):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    if tipo == "auto":
        esquina = rgb[2, 2]
        tipo = "blanco" if esquina.min() > 220 else "verde"
    if tipo == "verde":
        # La paleta no tiene verdes, así que cualquier píxel con dominante verde es fondo o
        # "derrame" del croma sobre el borde de la figura.
        return (g > 90) & (g > r * 1.35) & (g > b * 1.35)
    # Fondo blanco: no alcanza con buscar píxeles claros porque la cara y los guantes también
    # son blancos. Se toma sólo el blanco conectado con el borde de la imagen; el contorno de
    # tinta separa la figura del fondo y evita que el relleno "entre" en ella.
    claro = rgb.min(-1) > 225
    etiquetas, _ = ndi.label(claro)
    borde = np.unique(np.concatenate([etiquetas[0], etiquetas[-1],
                                      etiquetas[:, 0], etiquetas[:, -1]]))
    return np.isin(etiquetas, borde[borde > 0])


def cuantizar(rgb, permitidos):
    lab = rgb_a_lab(rgb.reshape(-1, 3).astype(np.float64))
    pal = rgb_a_lab(np.array([PALETA_RGB[i] for i in permitidos], dtype=np.float64))
    d = ((lab[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    idx = np.array(permitidos)[d.argmin(1)]
    return idx.reshape(rgb.shape[:2])


def separar_frames(fondo, columnas, filas):
    """Agrupa las manchas de la hoja por celda de la grilla (según su centroide)."""
    alto, ancho = fondo.shape
    figura = ~fondo
    etiquetas, n = ndi.label(figura)
    if n == 0:
        return []
    centros = ndi.center_of_mass(figura, etiquetas, range(1, n + 1))
    areas = ndi.sum(figura, etiquetas, range(1, n + 1))
    celdas = {}
    for k, ((cy, cx), area) in enumerate(zip(centros, areas), start=1):
        if area < 12:  # ruido de compresión
            continue
        col = min(int(cx / (ancho / columnas)), columnas - 1)
        fil = min(int(cy / (alto / filas)), filas - 1)
        celdas.setdefault(fil * columnas + col, []).append(k)
    frames = []
    for celda in sorted(celdas):
        m = np.isin(etiquetas, celdas[celda])
        ys, xs = np.nonzero(m)
        frames.append((m, (ys.min(), ys.max() + 1, xs.min(), xs.max() + 1)))
    return frames


def separar_por_valles(fondo, columnas, filas, margen=0.3):
    """Grilla con cortes ajustados: para figuras grandes que se tocan entre celdas vecinas.

    En las hojas del jefe la cola de una pose y la garra de la anterior se superponen, así que
    agrupar por manchas junta dos poses en un mismo frame. Cada línea de corte se busca cerca
    de su posición nominal, en la columna (o fila) con menos píxeles de figura: el "valle"
    entre dos poses. Lo poco que se corta ahí es una punta de cola o de garra, que se pierde
    menos que una pose entera.
    """
    alto, ancho = fondo.shape
    figura = ~fondo

    def cortes(perfil, n, largo):
        lineas = [0]
        for k in range(1, n):
            nominal = largo * k / n
            a = int(nominal - margen * largo / n)
            b = int(nominal + margen * largo / n)
            lineas.append(a + int(np.argmin(perfil[a:b])))
        return lineas + [largo]

    filas_c = cortes(figura.sum(1), filas, alto)
    frames = []
    for f in range(filas):
        y0, y1 = filas_c[f], filas_c[f + 1]
        cols_c = cortes(figura[y0:y1].sum(0), columnas, ancho)
        for c in range(columnas):
            x0, x1 = cols_c[c], cols_c[c + 1]
            m = np.zeros_like(figura)
            m[y0:y1, x0:x1] = figura[y0:y1, x0:x1]
            # Fuera de la mancha principal sólo se conservan piezas medianas (efectos, cartas):
            # el polvo de compresión y las puntas cortadas de la pose vecina se descartan.
            etiquetas, n = ndi.label(m)
            if n == 0:
                continue
            areas = np.asarray(ndi.sum(m, etiquetas, range(1, n + 1)))
            m = np.isin(etiquetas, [k + 1 for k in range(n) if areas[k] >= max(40, 0.02 * areas.max())])
            ys, xs = np.nonzero(m)
            frames.append((m, (ys.min(), ys.max() + 1, xs.min(), xs.max() + 1)))
    return frames


def integrales(indices, mascara):
    """Imágenes integrales por color: permiten contar los píxeles de cada bloque en O(1)."""
    def integral(m):
        ii = np.zeros((m.shape[0] + 1, m.shape[1] + 1), dtype=np.int64)
        ii[1:, 1:] = m.astype(np.int64).cumsum(0).cumsum(1)
        return ii
    clases = [int(c) for c in np.unique(indices[mascara])]
    return {"clases": clases,
            "por_clase": [integral(mascara & (indices == c)) for c in clases],
            "opacos": integral(mascara),
            "total": integral(np.ones_like(mascara))}


def separar_por_manchas(fondo, union=10, adjuntar=0.25):
    """Detecta cada figura sin depender de una grilla.

    Las hojas no siempre respetan una grilla de columnas pareja, así que las figuras se
    ubican por manchas: se dilata la máscara para que partes sueltas cercanas (sombrero en el
    aire, cartas, estrellas) queden unidas a su cuerpo, y las manchas chicas que siguen sueltas
    se asignan a la figura más cercana. El orden de lectura es por filas, de izquierda a
    derecha, igual que en la hoja.
    """
    figura = ~fondo
    dilatada = ndi.binary_dilation(figura, iterations=union)
    etiquetas, n = ndi.label(dilatada)
    if n == 0:
        return []
    areas = np.array(ndi.sum(figura, etiquetas, range(1, n + 1)))
    grandes = [k + 1 for k in range(n) if areas[k] >= 0.12 * areas.max()]
    grupos = {k: [k] for k in grandes}
    cajas = {k: ndi.find_objects((etiquetas == k).astype(int))[0] for k in grandes}
    altos = [cajas[k][0].stop - cajas[k][0].start for k in grandes]
    limite = adjuntar * float(np.median(altos))
    for k in range(1, n + 1):
        if k in grupos or areas[k - 1] < 30:
            continue
        ys, xs = np.nonzero(etiquetas == k)
        cy, cx = ys.mean(), xs.mean()
        mejor, dist = None, None
        for g in grandes:
            sy, sx = cajas[g]
            dy = max(sy.start - cy, 0, cy - sy.stop)
            dx = max(sx.start - cx, 0, cx - sx.stop)
            d = (dy * dy + dx * dx) ** 0.5
            if dist is None or d < dist:
                mejor, dist = g, d
        if dist is not None and dist <= limite:
            grupos[mejor].append(k)
    frames = []
    for g, ks in grupos.items():
        m = np.isin(etiquetas, ks) & figura
        ys, xs = np.nonzero(m)
        frames.append((m, (ys.min(), ys.max() + 1, xs.min(), xs.max() + 1)))
    # Orden de lectura: se agrupan en filas por solapamiento vertical.
    frames.sort(key=lambda f: (f[1][0] + f[1][1]) / 2)
    filas, actual = [], [frames[0]]
    for f in frames[1:]:
        ref = actual[0][1]
        centro = (f[1][0] + f[1][1]) / 2
        if ref[0] <= centro <= ref[1]:
            actual.append(f)
        else:
            filas.append(actual)
            actual = [f]
    filas.append(actual)
    return [f for fila in filas for f in sorted(fila, key=lambda f: f[1][2])]


def reducir_bloques(ii, forma, escala, fase_y, fase_x, alto_out, ancho_out, umbral_tinta):
    alto, ancho = forma
    ys = np.clip(np.round(fase_y + np.arange(alto_out + 1) * escala).astype(int), 0, alto)
    xs = np.clip(np.round(fase_x + np.arange(ancho_out + 1) * escala).astype(int), 0, ancho)

    def contar(m):
        return (m[ys[1:, None], xs[None, 1:]] - m[ys[:-1, None], xs[None, 1:]]
                - m[ys[1:, None], xs[None, :-1]] + m[ys[:-1, None], xs[None, :-1]])

    total = contar(ii["total"]).astype(np.float64)
    opacos = contar(ii["opacos"])
    out = np.full((alto_out, ancho_out), TRANSPARENTE, dtype=np.int32)
    if not ii["clases"]:
        return out, 0.0
    cuentas = np.stack([contar(m) for m in ii["por_clase"]])
    seguro = np.maximum(total, 1)
    elegido = np.array(ii["clases"])[cuentas.argmax(0)]
    pureza = cuentas.max(0) / seguro
    if INDICE_TINTA in ii["clases"]:
        tinta = cuentas[ii["clases"].index(INDICE_TINTA)]
        usa_tinta = tinta >= umbral_tinta * total
        elegido = np.where(usa_tinta, INDICE_TINTA, elegido)
        pureza = np.where(usa_tinta, tinta / seguro, pureza)
    transparente = (opacos < 0.5 * total) | (total == 0)
    out = np.where(transparente, TRANSPARENTE, elegido).astype(np.int32)
    pureza = np.where(transparente, 1 - opacos / seguro, pureza)
    return out, float(pureza.mean())


def limpiar(arte):
    opaco = arte != TRANSPARENTE
    vecinos = ndi.convolve(opaco.astype(int), np.ones((3, 3), int), mode="constant") - opaco
    # Píxeles opacos sin ningún vecino: polvo que deja la compresión de la imagen original.
    arte[opaco & (vecinos == 0)] = TRANSPARENTE
    # Agujeros de un píxel rodeados en cruz por la figura: se rellenan con el color vecino
    # más frecuente (los huecos reales del dibujo, como entre brazo y torso, son más grandes).
    opaco = arte != TRANSPARENTE
    cruz = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    rodeado = ndi.convolve(opaco.astype(int), cruz, mode="constant") == 4
    for y, x in zip(*np.nonzero(~opaco & rodeado)):
        vec = [arte[y - 1, x], arte[y + 1, x], arte[y, x - 1], arte[y, x + 1]]
        arte[y, x] = max(set(vec), key=vec.count)
    return arte


def contorno_selectivo(arte, oscuros, borde, relleno):
    """Separa contorno y relleno dentro de las masas oscuras.

    En las hojas la levita y la galera están casi del mismo negro que el contorno, y a 48 px
    eso se lee como una mancha sin volumen. Se aplica la convención clásica del pixel art: el
    borde de la masa oscura (lo que toca el fondo o un color claro) queda en tinta, y el
    interior pasa al negro de relleno, un escalón más claro.
    """
    es_oscuro = np.isin(arte, oscuros)
    pad = np.pad(es_oscuro, 1, constant_values=False)
    vecinos_oscuros = (pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    nuevo = arte.copy()
    nuevo[es_oscuro & ~vecinos_oscuros] = borde
    nuevo[es_oscuro & vecinos_oscuros] = relleno
    return nuevo


def a_imagen(arte):
    rgba = np.zeros(arte.shape + (4,), dtype=np.uint8)
    for k in np.unique(arte):
        if k == TRANSPARENTE:
            continue
        rgba[arte == k] = (*PALETA_RGB[k], 255)
    return Image.fromarray(rgba)


def colocar(arte, lienzo_w, lienzo_h, ancla_v, ancla_h, base, techo, centro_x):
    alto, ancho = arte.shape
    ys, xs = np.nonzero(arte != TRANSPARENTE)
    if ancla_h == "cabeza":
        # Centro horizontal de la parte superior de la figura (galera + cabeza): es lo que el
        # ojo sigue, así el cuerpo puede balancearse sin que el personaje parezca desplazarse.
        corte = ys.min() + max(int((ys.max() - ys.min()) * 0.3), 1)
        cx = xs[ys <= corte].mean()
    else:
        cx = (xs.min() + xs.max()) / 2
    dx = int(round(centro_x - cx))
    if ancla_v == "pies":
        dy = base - ys.max()
    elif ancla_v == "cabeza":
        dy = techo - ys.min()
    else:
        # Giros en el aire: se fija el centro de la figura en el centro del cuerpo de pie, así
        # la rotación ocurre "en el lugar" y no alrededor de los pies.
        dy = int(round((techo + base) / 2 - (ys.min() + ys.max()) / 2))
    lienzo = np.full((lienzo_h, lienzo_w), TRANSPARENTE, dtype=np.int32)
    recorte = 0
    for y, x in zip(ys, xs):
        ny, nx = y + dy, x + dx
        if 0 <= ny < lienzo_h and 0 <= nx < lienzo_w:
            lienzo[ny, nx] = arte[y, x]
        else:
            recorte += 1
    return lienzo, recorte


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hoja")
    ap.add_argument("salida")
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--columnas", type=int, default=None, help="sin columnas/filas: por manchas")
    ap.add_argument("--filas", type=int, default=None)
    ap.add_argument("--valles", action="store_true",
                    help="con columnas/filas: cortar la grilla en los valles entre figuras")
    ap.add_argument("--fondo", choices=["auto", "verde", "blanco", "alfa"], default="auto")
    ap.add_argument("--union", type=int, default=10, help="distancia para unir partes sueltas")
    ap.add_argument("--borrar", type=int, nargs=4, action="append", metavar=("X0", "Y0", "X1", "Y1"),
                    help="zona de la hoja a descartar (manchas o restos)")
    ap.add_argument("--alto", type=int, default=48, help="alto en píxeles de la pose de pie")
    ap.add_argument("--lienzo", type=int, nargs=2, default=[64, 64], metavar=("ANCHO", "ALTO"))
    ap.add_argument("--referencia", type=int, default=None,
                    help="índice del frame de pie usado sólo para medir la escala (se descarta)")
    ap.add_argument("--escala", type=float, default=None, help="escala fija (px fuente por px)")
    ap.add_argument("--usar", type=int, nargs="*", default=None, help="frames a exportar, en orden")
    ap.add_argument("--ancla-v", choices=["pies", "cabeza", "centro"], default="pies")
    ap.add_argument("--ancla-h", choices=["cabeza", "caja"], default="cabeza")
    ap.add_argument("--base", type=int, default=None, help="fila de los pies en el lienzo")
    ap.add_argument("--centro-x", type=float, default=None)
    ap.add_argument("--colores", nargs="*", default=None, help="subconjunto de la paleta")
    ap.add_argument("--umbral-tinta", type=float, default=0.42)
    ap.add_argument("--suavizar", type=int, default=5, help="tamaño del filtro de mediana previo")
    ap.add_argument("--contorno-selectivo", action="store_true")
    args = ap.parse_args()

    lienzo_w, lienzo_h = args.lienzo
    base = args.base if args.base is not None else lienzo_h - 2
    techo = base - args.alto + 1
    centro_x = args.centro_x if args.centro_x is not None else lienzo_w / 2

    original = Image.open(args.hoja)
    rgb = np.asarray(original.convert("RGB")).astype(np.float64)
    alfa = np.asarray(original.convert("RGBA"))[..., 3] if "A" in original.getbands() else None
    if args.suavizar:
        # Mediana por canal: borra el "granulado" de compresión sin redondear los bordes
        # duros, que es lo que importa conservar en pixel art.
        rgb = ndi.median_filter(rgb, size=(args.suavizar, args.suavizar, 1))
    if args.fondo == "alfa" or (args.fondo == "auto" and alfa is not None and alfa.min() < 128):
        # Poses ya recortadas sobre fondo transparente (arte previo del proyecto).
        fondo = alfa < 128
    else:
        fondo = mascara_fondo(rgb, args.fondo)
    fondo = ndi.binary_opening(fondo, iterations=1)
    # Líneas de grilla que separan las celdas en algunas hojas. Se reconocen
    # porque cruzan la hoja entera sin cortes; dos figuras apiladas en la misma columna también
    # suman mucho alto, pero dejan un hueco entre filas.
    def tramo_mas_largo(v):
        bordes = np.diff(np.concatenate([[0], v.astype(np.int8), [0]]))
        inicios, fines = np.nonzero(bordes == 1)[0], np.nonzero(bordes == -1)[0]
        return int((fines - inicios).max()) if len(inicios) else 0
    figura = ~fondo
    for y in np.nonzero(figura.mean(1) > 0.9)[0]:
        if tramo_mas_largo(figura[y]) >= 0.97 * figura.shape[1]:
            fondo[y, :] = True
    for x in np.nonzero(figura.mean(0) > 0.9)[0]:
        if tramo_mas_largo(figura[:, x]) >= 0.97 * figura.shape[0]:
            fondo[:, x] = True
    for zona in args.borrar or []:
        x0, y0, x1, y1 = zona
        fondo[y0:y1, x0:x1] = True
    permitidos = ([NOMBRES.index(c) for c in args.colores] if args.colores
                  else list(range(len(NOMBRES))))
    indices = cuantizar(rgb, permitidos)

    if args.columnas and args.filas and args.valles:
        frames = separar_por_valles(fondo, args.columnas, args.filas)
    elif args.columnas and args.filas:
        frames = separar_frames(fondo, args.columnas, args.filas)
    else:
        frames = separar_por_manchas(fondo, union=args.union)
    alturas = [int(b[1] - b[0]) for _, b in frames]
    if args.escala:
        escala = args.escala
    elif args.referencia is not None:
        escala = alturas[args.referencia] / args.alto
    else:
        escala = float(np.median(alturas)) / args.alto

    orden = args.usar if args.usar is not None else [
        i for i in range(len(frames)) if i != args.referencia]

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    imagenes, informe = [], []
    for n, i in enumerate(orden):
        m, (y0, y1, x0, x1) = frames[i]
        pad = int(escala * 2)
        y0, x0 = max(y0 - pad, 0), max(x0 - pad, 0)
        y1, x1 = min(y1 + pad, rgb.shape[0]), min(x1 + pad, rgb.shape[1])
        sub_idx, sub_m = indices[y0:y1, x0:x1], m[y0:y1, x0:x1] & ~fondo[y0:y1, x0:x1]
        alto_out = int(np.ceil((y1 - y0) / escala)) + 1
        ancho_out = int(np.ceil((x1 - x0) / escala)) + 1
        ii = integrales(sub_idx, sub_m)
        mejor = None
        for fy in np.linspace(-escala / 2, escala / 2, 8, endpoint=False):
            for fx in np.linspace(-escala / 2, escala / 2, 8, endpoint=False):
                arte, pureza = reducir_bloques(ii, sub_idx.shape, escala, fy, fx,
                                               alto_out, ancho_out, args.umbral_tinta)
                if mejor is None or pureza > mejor[1]:
                    mejor = (arte, pureza)
        arte = limpiar(mejor[0])
        if args.contorno_selectivo:
            arte = contorno_selectivo(arte, [INDICE_TINTA, NOMBRES.index("levita")],
                                      INDICE_TINTA, NOMBRES.index("levita"))
        lienzo, recorte = colocar(arte, lienzo_w, lienzo_h, args.ancla_v, args.ancla_h,
                                  base, techo, centro_x)
        img = a_imagen(lienzo)
        img.save(salida / f"{args.nombre}_{n + 1}.png")
        imagenes.append(img)
        informe.append({"frame": n + 1, "origen": i, "pureza": round(mejor[1], 3),
                        "pixeles_recortados": int(recorte)})

    # Vista previa ampliada x4 sobre gris medio, para revisar a ojo (no se usa en el juego).
    zoom = 4
    fondo_prev = (90, 86, 98, 255)
    tira = Image.new("RGBA", (lienzo_w * len(imagenes) * zoom, lienzo_h * zoom), fondo_prev)
    cuadros = []
    for n, img in enumerate(imagenes):
        grande = img.resize((lienzo_w * zoom, lienzo_h * zoom), Image.NEAREST)
        tira.alpha_composite(grande, (n * lienzo_w * zoom, 0))
        cuadro = Image.new("RGBA", grande.size, fondo_prev)
        cuadro.alpha_composite(grande)
        cuadros.append(cuadro.convert("P", palette=Image.ADAPTIVE))
    tira.save(salida / f"_preview_{args.nombre}.png")
    if cuadros:
        cuadros[0].save(salida / f"_preview_{args.nombre}.gif", save_all=True,
                        append_images=cuadros[1:], duration=110, loop=0, disposal=2)
    print(json.dumps({"nombre": args.nombre, "frames_detectados": len(frames),
                      "alturas_fuente": alturas, "escala": round(escala, 3),
                      "frames": informe}, ensure_ascii=False))


if __name__ == "__main__":
    main()
