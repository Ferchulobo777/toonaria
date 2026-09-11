# 11 — Ambrosio Lobo: hoja de poses de combate (NUEVO — pendiente)

**Guardar como**: `arte/ambrosio-lobo-hoja-combate.jpg`, después recortar en poses individuales
igual que se hizo con Ventura.

**Por qué hace falta ahora**: el combate del jefe ya está diseñado en `GDD.md` — 2 fases
(Farolero/Lobo), 3 ataques con telegraph (Embestida, Zarpazo, Aullido) y una transición de fase
donde parpadea a su forma humana. Faltan las poses para poder implementarlo en GDevelop.

**Cómo generarlo**: adjuntar `ambrosio-lobo.jpg` (la referencia ya aprobada) como imagen de
referencia junto con este prompt, para mantener el mismo diseño.

```
Using the attached reference image of the werewolf boss character
exactly as designed (same silhouette, fur rendering, torn coat,
glowing eyes, color palette — do not redesign), create a character
pose reference sheet with 5 side-by-side full-body poses of the SAME
character, 1930s rubber-hose cartoon style, flat dark gray background,
consistent scale across all poses:

1. Idle/guard stance — hunched, alert, low growl, ready to react.
2. Embestida (charge) telegraph — crouched low, muscles coiled,
   gathering momentum, a beat before lunging forward.
3. Zarpazo (claw swipe) — one oversized clawed hand raised high mid-
   swing, a faint moonlight glint along the claws as the telegraph cue.
4. Aullido (howl) — reared up on hind legs, head thrown back howling,
   a faint pale shockwave ring starting to expand from the ground
   around him.
5. Phase transition — a brief flicker back toward his human silhouette
   (Ambrosio, the lamplighter), ghostly and translucent, overlaid on
   the wolf form, as if the curse is losing grip for a split second.

Label each pose faintly underneath (Guardia, Embestida, Zarpazo,
Aullido, Transicion). Clean flat cel-shaded coloring, character
reference sheet style, toon-horror tone, not gory.
```

## Después de generarla

Mismo proceso que con `mov.jpg` de Ventura: recortar cada pose (fondo plano, se puede
automatizar) y guardarlas como frames de las animaciones del objeto `AmbrosioLobo` en GDevelop
(Guardia, Embestida, Zarpazo, Aullido, Transicion) — matchean directo con los nombres de ataque
ya definidos en el GDD.
