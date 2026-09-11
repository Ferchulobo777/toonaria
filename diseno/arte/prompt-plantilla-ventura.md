# Prompt — hoja de poses de Ventura (rediseño de cabeza + espaciado real)

Prompt listo para pegar en la herramienta de generación de imágenes que se use para el arte de
Ventura. Reemplaza a `mov.jpg`, `ventura-hoja-doble-salto-parry.jpg` y `ventura-derrota.jpg`
como fuente — **las 14 animaciones que usa el personaje en `game.json`, en una sola hoja**, no
un lote principal más lotes sueltos después. Resuelve tres cosas a la vez:

1. **Espaciado real entre poses.** `mov.jpg` tenía las 8 poses de la fila de arriba literalmente
   pegadas entre sí (confirmado a nivel de píxel al auditar el recorte, ver `GDD.md` — "Cuarta
   tanda" del 2026-09-02): el recorte automático y hasta el manual terminaban agarrando fragmentos
   de la pose vecina. La causa raíz era la plantilla de origen, no el método de recorte.
2. **Diseño de cabeza pendiente.** El GDD tenía marcado como advertencia (línea 105) que la cabeza
   del concept actual (`ventura.jpg`) se parece demasiado a Bendy (*Bendy and the Ink Machine*) —
   orejas curvas tipo cuerno, ojos de botón negros, sonrisa enorme — de forma puntual, no como
   influencia genérica del estilo rubber-hose. Había que resolverlo antes de sprites finales.
3. **Una sola cabeza consistente en las 14 poses.** `SaltoDoble` (giro-bola), `Parry` y
   `Derrota` se habían generado en lotes separados y usan la cabeza vieja — quedaban
   inconsistentes con el resto apenas se rediseñe la cara. Este prompt las incluye todas juntas
   para que las 14 salgan con la misma cara de una sola vez.

**Una sola dirección, nunca se generan las dos.** El juego mira siempre hacia la derecha en el
arte y se da vuelta con un flip horizontal 2D nativo del motor (acción `FlipX` de GDevelop, ya
usada en `Level1` y `ArenaJefe` para las teclas Izquierda/Derecha — confirmado en `game.json`).
Esto aplica a las 14 poses sin excepción, incluidas las que "giran" o "retroceden" en el gameplay
(`Parry`, `Recuperación`, etc.): ninguna necesita una versión mirando para el otro lado, todas se
dibujan una sola vez mirando a la derecha y el motor las espeja cuando hace falta. Decisión
confirmada 2026-09-02 después de evaluar la alternativa (duplicar a 28 poses) — no vale la pena,
`FlipX` ya está probado y andando.

> [!warning] Primer intento (2026-09-02) falló en dos cosas puntuales
> Se probó este prompt y el resultado no sirvió: (1) el generador metió texto igual (título
> "VENTURA" arriba y una leyenda debajo de cada pose — "Walking Right", "Tipping hat", etc.,
> pese a la instrucción explícita de no incluir texto) y (2) ignoró la lista de 14 poses y
> devolvió una hoja de personaje genérica (poses tipo "Sitting", "Bowing", "Tipping hat",
> "Expression Sheet" que no son ninguna de las 14 que necesita el juego). El prompt de abajo ya
> quedó reforzado contra los dos problemas — repite la prohibición de texto al principio Y al
> final, y aclara explícitamente que no se acepta sustituir/agregar poses genéricas. Si se repite
> el problema, la salida recomendada es generar en 2-3 tandas más chicas (ej. filas 1-2 en una
> pasada, filas 3-4 en otra) reusando la misma descripción de personaje/cabeza en cada una —
> los generadores de imagen suelen respetar mejor listas cortas que una de 14 puntos.

**Lo que NO cambia** (ya aprobado, sostener en el prompt tal cual): vestuario gótico-victoriano —
levita negra larga con cola/capa, chaleco crema/hueso, moño morado, galera de ala ancha con
símbolo de luna creciente, guantes blancos, botas de dos tonos (crema y negro), farol antiguo
como prop situacional (no siempre en mano), mazo de cartas moradas con símbolo de luna. Paleta:
blanco y negro con acentos de color (principalmente el morado del brillo mágico de las cartas).
Estilo: cartoon clásico rubber-hose, línea de tinta limpia, coloreado plano.

---

## Prompt

```
ABSOLUTE RULE, read this first: this image must contain ONLY character artwork on a flat
background. NO text of any kind anywhere in the image — no title, no character name, no pose
labels, no captions under each pose, no numbers, no speech bubbles, no watermark, nothing
written at all, not even one word. If you are tempted to add a caption under a pose to clarify
what it is, do not — the pose description below is only for you to draw the right action, it
must never appear as visible text in the output image.

STRICT POSE LIST RULE: generate EXACTLY the 14 poses listed below, in EXACTLY this order and
with EXACTLY these actions — do not substitute, skip, merge, reorder, or add any extra generic
poses of your own (no "sitting", "bowing", "tipping hat", "leaning", "pointing", "sneaking",
"expression sheet", or any other pose not explicitly listed below). This is a game sprite sheet
for a real game engine, not a general character exploration/turnaround sheet — every single one
of the 14 poses listed must be present, and nothing else.

Character reference sheet, rubber-hose cartoon style (1930s classic cartoon proportions,
clean black ink outlines, flat cel shading, no gradients), black-and-white color palette
with sparse purple magical accent color only on the cards and their glow.

CHARACTER: "Ventura", a young gentleman cartomancer/fortune-teller in a gothic-Victorian
setting. Slim rubber-hose body proportions, pale ink-white skin.

Outfit (keep exactly, do not redesign): long black tailcoat with a flowing coat-tail/cape,
cream/off-white waistcoat with dark buttons, a purple bow tie, a wide-brimmed black gambler
hat with a thin crescent-moon charm on the band, white gloves, two-tone shoes (cream and
black), slim black trousers. He carries a deck of purple playing cards marked with a
crescent-moon symbol, and has an antique brass lantern as a situational prop (not always
in hand).

FACE / HEAD — new design, must NOT resemble Bendy (Bendy and the Ink Machine) or any other
existing cartoon-horror mascot. Specifically avoid: curved horn-shaped ears, solid black
circular button eyes with no visible iris, a permanently wide open-mouthed toothy grin.
Instead: no visible ears (fully covered by the wide hat brim at every angle), large
expressive almond-shaped eyes with a visible iris (warm dark brown or a subtle violet tint)
and visible eyebrows for real expression, a confident closed or half-closed sly smirk
(showman's smile, at most a hint of teeth, never a full open grin), a thin pencil mustache
above the lip as a small distinguishing signature feature. Keep the head round and friendly
in the rubber-hose tradition, just with this specific face design, consistent across every
single pose below — same face, same hat, same proportions, only the pose changes.

ORIENTATION: the character faces and moves toward the RIGHT of the frame in every single
pose, no exceptions, including poses that represent turning, blocking, recovering or falling.
Do not generate a mirrored/left-facing version of anything, and do not generate a "turned
around" or back-facing pose for any action — every reversal or direction change in the actual
game is a plain horizontal flip of the same single right-facing artwork done live by the game
engine, so a left-facing or back-facing pose would be wasted art and must not be included.

POSES NEEDED (14 total, one per grid cell, in this exact reading order left-to-right,
top-to-bottom in a 4-column grid, 4 rows):

Row 1:
1. "Idle" — relaxed standing pose, weight on one leg, cards held loosely fanned in one hand,
   calm confident posture.
2. "Carga 1" — starting to charge a card: one card raised near chest height, a faint small
   glow just beginning at its tip.
3. "Carga 2" — mid-charge: the card glows brighter, a visible small purple energy swirl around
   it, more tension in the pose (leaning slightly, focused expression).
4. "Carga completa" — full charge: the card and hand engulfed in a bright purple glow with
   small magic particles/sparks radiating outward, dramatic ready-to-throw stance.

Row 2:
5. "Correr" (running/walking) — mid-stride action pose, one leg forward one leg back, arms
   pumping, coat-tail flowing behind from the motion, dynamic and clearly different from Idle.
6. "Salto inicio" (jump start / crouch) — knees bent low, arms pulled back, about to push off
   the ground, anticipation pose.
7. "Salto aire" (mid-air) — fully airborne, legs tucked or trailing below, arms up, coat
   billowing upward, floating/weightless feeling, feet not touching any ground line.
8. "Aterrizaje" (landing) — knees deeply bent absorbing impact, arms out for balance, coat-tail
   settling down, low crouch just after touching ground.

Row 3:
9. "Arrojar" (throwing) — dynamic throwing follow-through, arm extended forward-right releasing
   a glowing purple card, weight shifted onto the front foot, other arm trailing back for
   balance.
10. "Recibir daño" (hit reaction) — flinching backward, eyes shut or wincing, one arm raised
    defensively, off-balance stumbling pose, hat slightly knocked askew.
11. "Recuperación" (recovering) — steadying stance right after the hit, one hand on the ground
    or knee for balance, determined expression looking back up, about to stand back up.
12. "Salto doble" (mid-air spin/tuck) — the character curled into a tight aerodynamic ball,
    knees pulled to chest, arms wrapped in, coat and hat tucked into the spin, used as a second
    airborne jump — same energetic mid-air feeling as "Salto aire" but tucked into a roll
    instead of open.

Row 4 (only 2 poses — leave the other 2 cells of this row empty, do not fill them with
anything):
13. "Parry" — a sharp defensive lunge stance, weight shifted low and forward, one arm thrust
    out holding a single card up as a shield/deflector, a small bright spark or flash right at
    the card where it intercepts an incoming attack, focused alert expression, cape whipping
    from the sudden motion.
14. "Derrota" (defeated) — collapsed flat on the ground face-up, arms splayed out to the
    sides, hat knocked off and lying separately nearby, several cards scattered loose on the
    ground around him, eyes shown closed or as a defeated "x" mark, an exhausted slack
    expression, lantern resting on the ground beside him.

LAYOUT REQUIREMENTS (critical, previous attempts failed on this):
- Arrange the 14 poses in a strict 4-column grid (3 full rows of 4, last row only 2 filled).
- Each pose occupies its own cell with a fixed, identical cell size across the whole sheet.
- Leave a WIDE empty gutter between every cell — minimum 20% of the character's own width as
  clear empty space on every side of each pose. No pose's silhouette, limb, cape, card, or
  held prop may extend into a neighboring cell or touch/overlap any other pose at any point.
  This is the single most important requirement of this sheet.
- All 14 poses must share the exact same character scale (same head-to-toe height in pixels)
  and the same ground baseline (feet at the same Y position within each cell for grounded/
  standing poses; "Salto aire", "Salto doble" and "Derrota" are the expected exceptions since
  they are airborne or on the ground by design), so they can be cropped and used as game
  sprites without manual rescaling.
- Flat, even, shadowless lighting identical across every pose (no per-pose dramatic lighting
  changes) — this is for a game sprite sheet, not illustration.

BACKGROUND: a single flat solid background color for the entire sheet, one that does not
appear anywhere in the character's own palette (not gray, not black, not white, not purple) —
use a flat bright green (#00FF00) or flat magenta (#FF00FF) so the character can be
automatically separated from the background by color-key with zero ambiguity.

DO NOT include: any text, labels, captions, pose names, numbers, watermarks, or UI elements
anywhere in the image — the image must contain ONLY the 14 character poses on the flat
background, nothing else.

Output as a single high-resolution image, poses large enough that facial details and card
glow are clearly legible.

FINAL CHECK before you output the image: confirm there is zero text anywhere in the image
(no title, no pose captions, no watermark), and confirm the image shows exactly these 14
poses and no others — Idle, Carga 1, Carga 2, Carga completa, Correr, Salto inicio, Salto
aire, Aterrizaje, Arrojar, Recibir daño, Recuperación, Salto doble, Parry, Derrota.
```

---

## Después de generar

- Recortar cada pose igual que se hizo con la tanda anterior (componentes conexos sobre un fondo
  plano da resultados mucho más limpios que sobre `mov.jpg` — con este fondo saturado y sin
  bordes tocándose debería alcanzar con un recorte directo por color, sin falta de separar blobs
  fusionados).
- Reemplazar las 14 imágenes en `juego/assets/ventura/` (11 de `mov.jpg` + `ventura_doble_salto`,
  `ventura_parry`, `ventura_derrota`) y volver a correr `preview_scene` sobre `Level1` y
  `ArenaJefe` para confirmar en el motor real, mismo criterio que las tandas anteriores — no
  alcanza con verlo bien en la imagen generada sola.
