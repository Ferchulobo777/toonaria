# 15 — Ambrosio Lobo: pose de ataque "Garra de luna" (NUEVO — pendiente)

**Guardar como**: `arte/ambrosio-lobo-garra-de-luna.jpg`, después recortar igual que el resto de
las poses del jefe (ver `arte/ambrosio-lobo-sprites/`).

**Por qué hace falta ahora**: la revisión del 2026-09-02 del GDD suma un cuarto ataque a la fase
2 del jefe — Garra de luna, proyectiles de luz lunar morada (mismo símbolo que las cartas de
Ventura) que se pueden parryear. La hoja de combate ya generada (`hoja de combate-lobo.jpg`,
prompt 11) cubre Guardia/Embestida/Zarpazo/Aullido/Transicion — no tiene esta pose nueva.

**Cómo generarlo**: adjuntar `ambrosio-lobo.jpg` (la referencia base ya aprobada) como imagen de
referencia junto con este prompt, para mantener el mismo diseño y paleta que el resto de las
poses de combate.

```
Using the attached reference image of the werewolf boss character
exactly as designed (same silhouette, fur rendering, torn coat, glowing
eyes, color palette — do not redesign), create a single full-body
action pose of the SAME character, 1930s rubber-hose cartoon style,
flat dark gray background, same scale as a typical combat pose sheet:

Garra de luna (moon claw) — both clawed hands drawn together in front
of his chest, palms glowing with the same purple moonlight as the
card-throwing magic used against him, small crescent-moon symbols
glinting faintly within the glow, a beat before unleashing it forward.
The purple glow should read as clearly corrupted/stolen version of the
player's own card magic — same hue and moon-symbol motif, not a
different color.

Label the pose faintly underneath (Garra de Luna). Clean flat
cel-shaded coloring, character reference sheet style, toon-horror
tone, not gory.
```

## Después de generarla

Recortar la pose (fondo plano) y agregarla como una animación nueva más (`GarraDeLuna`) del
objeto `AmbrosioLobo` ya existente en GDevelop, junto a las otras 5.
