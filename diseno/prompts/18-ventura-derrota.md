# 18 — Ventura: pose de derrota / tirado en el suelo (NUEVO — pendiente)

**Guardar como**: `arte/ventura-derrota.jpg`, después recortar igual que el resto (ver
`arte/ventura-sprites/`).

**Por qué hace falta ahora**: hasta ahora Ventura tenía `RecibirDano` (flinch de golpe) pero
nada para cuando la vida llega a 0 — la lógica de muerte/respawn ya está implementada en
GDevelop (ver `game.json`) pero usa `RecibirDano` como reemplazo temporal porque todavía no
existe una pose de derrota real.

**Cómo generarlo**: adjuntar `ventura.jpg` (la referencia ya aprobada) como imagen de
referencia junto con este prompt.

```
Using the attached reference image of the character exactly as
designed (same face, hat, outfit, colors, proportions — do not
redesign the character), create a single full-body pose of the SAME
character, 1930s rubber-hose cartoon style, flat mid-gray background,
same scale as a typical pose reference:

Defeated/knocked down — sprawled on his back on the ground, hat
knocked off and lying beside him, cards scattered loosely around him,
eyes shown as X's or swirls (classic cartoon "knocked out" convention),
one arm flopped to the side. Should read clearly as comedic-cartoon
defeat, not grim or violent — matches the toon tone of the rest of the
game, not Bloodborne's grimness.

Label the pose faintly underneath (Derrota). Clean flat cel-shaded
coloring, character reference sheet style.
```

## Después de generarla

Recortar (fondo plano) y guardar en `arte/ventura-sprites/derrota.png` — reemplaza el
placeholder (`RecibirDano` reciclado) en la animación `Derrota` del objeto `Player` en
GDevelop. Como es una pose tirada en el suelo, probablemente necesite un ajuste de
`originPoint`/posición Y al importarla (el personaje pasa de estar parado a estar acostado, así
que el punto de referencia para plantarlo en el piso cambia).
