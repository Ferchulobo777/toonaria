# 10 — Ventura: hojas de pose por acción (sprite sheet)

**Guardar como**: 3 hojas separadas, o todas juntas como pasó la última vez —
✅ ya cubierto por `arte/mov.jpg`, ya recortado en 11 poses individuales dentro de
`arte/ventura-sprites/`. Este archivo queda solo para regenerar alguna pose puntual que salga
mal (por ejemplo si en algún momento se rehace `ventura.jpg` con la cara rediseñada de nuevo).

> [!tip] Por qué "hojas" y no frames sueltos
> Pedir cada pose en una generación separada hace que el personaje derive un poco cada vez.
> Pedir varias poses juntas EN UNA SOLA generación, adjuntando `ventura.jpg` como imagen de
> referencia, da mucha más consistencia.

**Cómo generarlas**: adjuntar `ventura.jpg` como imagen de referencia junto con el prompt (el
modelo debe editar/componer a partir de esa imagen, no generar desde cero).

### Hoja 1 — Idle y carga de carta

```
Using the attached reference image of the character exactly as
designed (same face, hat, outfit, colors, proportions — do not
redesign the character), create a character pose reference sheet with
4 side-by-side full-body poses of the SAME character, 1930s
rubber-hose cartoon style, flat mid-gray background, consistent scale
across all 4 poses:

1. Idle stance — relaxed standing pose, cards fanned loosely in one
   hand, weight shifted slightly to one leg.
2. Charging a card, stage 1 (light charge) — one card held out,
   glowing faintly with a soft purple-white light.
3. Charging a card, stage 2 (medium charge) — same pose, the glow
   brighter and slightly larger.
4. Charging a card, stage 3 (full charge) — same pose, the glow
   intense, small sparks/particles around the card.

Label each pose faintly underneath (Idle, Carga 1, Carga 2, Carga
Completa). Clean flat cel-shaded coloring, character reference sheet
style.
```

### Hoja 2 — Movimiento (correr y saltar)

```
Using the attached reference image of the character exactly as
designed (same face, hat, outfit, colors, proportions — do not
redesign the character), create a character pose reference sheet with
4 side-by-side full-body poses of the SAME character, 1930s
rubber-hose cartoon style, flat mid-gray background, consistent scale
across all 4 poses:

1. Running — mid-stride action pose, coat tails and cape flowing
   behind from the motion.
2. Jump start — crouched about to leap, arms swinging back.
3. Jump apex/falling — airborne pose, legs tucked, arms out for
   balance.
4. Landing — crouched landing pose absorbing impact.

Label each pose faintly underneath (Correr, Salto-Inicio, Salto-Aire,
Aterrizaje). Clean flat cel-shaded coloring, character reference sheet
style.
```

### Hoja 3 — Combate (arrojar y recibir daño)

```
Using the attached reference image of the character exactly as
designed (same face, hat, outfit, colors, proportions — do not
redesign the character), create a character pose reference sheet with
3 side-by-side full-body poses of the SAME character, 1930s
rubber-hose cartoon style, flat mid-gray background, consistent scale
across all poses:

1. Throwing a card — dynamic release pose, arm extended forward, one
   glowing card flying out of frame toward the viewer.
2. Hit reaction — recoiling pose, flinching backward, hat tilted
   slightly, one hand raised defensively.
3. Recovering — slightly hunched but alert stance, cards being
   reshuffled/regrouped, ready to act again.

Label each pose faintly underneath (Arrojar, Recibir Daño,
Recuperación). Clean flat cel-shaded coloring, character reference
sheet style.
```

### Después de generarlas

1. Recortar cada pose como imagen individual con fondo transparente — [Photopea](https://www.photopea.com)
   (gratis, en el navegador) o pedirme que lo automatice como la vez pasada (con Python/PIL,
   detectando el fondo plano).
2. Importar cada recorte como frame suelto en la animación correspondiente del objeto Sprite en
   GDevelop — no hace falta una grilla prearmada.
