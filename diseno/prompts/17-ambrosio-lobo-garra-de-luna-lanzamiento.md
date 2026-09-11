# 17 — Ambrosio Lobo: pose de lanzamiento de "Garra de luna" (NUEVO — pendiente)

**Guardar como**: `arte/ambrosio-lobo-garra-de-luna-lanzamiento.jpg`, después recortar igual que
el resto de las poses del jefe.

**Por qué hace falta ahora**: la pose del prompt 15 (ya generada, `ambrosio-lobo-garra-de-luna.jpg`)
muestra al jefe *cargando* el ataque — las garras juntas al pecho, todavía sin soltarlo. Falta
el frame de *lanzamiento*, el mismo criterio que ya se usó con Ventura (que tiene una pose
`Carga` y una pose `Arrojar` separadas, no solo una). Sin este frame, en el juego el proyectil
`GarraLuna` va a aparecer "de la nada" en vez de salir visiblemente de las manos del jefe.

**Cómo generarlo**: adjuntar `ambrosio-lobo-garra-de-luna.jpg` (la pose de carga ya aprobada,
prompt 15) como imagen de referencia junto con este prompt — mismo personaje, continuación
directa del mismo gesto.

```
Using the attached reference image of the werewolf boss character in
mid-cast pose exactly as designed (same silhouette, fur rendering,
torn coat, glowing eyes, purple moon-magic color palette — do not
redesign), create a single full-body action pose of the SAME
character, continuing directly from the same gesture, 1930s
rubber-hose cartoon style, flat dark gray background, same scale as
the reference:

Garra de luna — lanzamiento (release) — both arms now thrust forward
toward the viewer, claws splayed open, releasing the built-up purple
moonlight energy as a claw-shaped projectile bursting forward out of
his hands. Wider stance, weight thrown forward into the motion, a
brighter flash right at the point of release.

Label the pose faintly underneath (Garra de Luna - Lanzamiento). Clean
flat cel-shaded coloring, character reference sheet style, toon-horror
tone, not gory.
```

## Después de generarla

Recortar la pose (fondo plano) y agregarla como una animación más (`GarraDeLunaLanzamiento`) del
objeto `AmbrosioLobo` en GDevelop, junto a `GarraDeLuna` (carga) y las otras 5 ya importadas —
son las dos mitades del mismo ataque, igual que `Carga1`/`Carga2`/`CargaCompleta` + `Arrojar` en
Ventura.
