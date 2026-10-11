"""Paleta cerrada de Toonaria.

Extiende la paleta de 8 colores de la ficha de pixel art (Unidad 4) con los tonos de sombra
necesarios para sombrear a dos tonos por material, más los grises de tinta para escenarios y
dos acentos con función narrativa: el ámbar del farol (único color cálido del juego, asociado a
Ambrosio) y el plateado-azulado del Repintado (la "tinta de luna" que corrompe a los toons).
El morado sigue siendo el único acento de Ventura.
"""

PALETA_HEX = {
    # Tinta (contornos y negros) — base de la ficha
    "tinta": "#121014",
    "levita": "#221F26",
    "gris_oscuro": "#3A3541",
    "gris_medio": "#5D5766",
    "gris": "#8C8695",
    "gris_claro": "#BDB7C4",
    "blanco": "#FFFFFF",
    # Piel y crema — base de la ficha + sombra
    "piel": "#F5E7D4",
    "piel_sombra": "#D8C2AA",
    "crema": "#E7D6AD",
    "crema_sombra": "#B9A47A",
    # Morado lunar — acento de Ventura
    "morado_oscuro": "#46276E",
    "morado": "#6B3FA0",
    "morado_claro": "#B085D6",
    "luna": "#EEE2F6",
    # Ámbar del farol
    "bronce": "#8A5A2B",
    "ambar": "#C08A3A",
    "llama": "#F6C760",
    # Tinta de luna del Repintado
    "plata_oscura": "#4E6E8E",
    "plata": "#9FC3E6",
}


def hex_a_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


PALETA_RGB = [hex_a_rgb(h) for h in PALETA_HEX.values()]
NOMBRES = list(PALETA_HEX.keys())
INDICE_TINTA = NOMBRES.index("tinta")
