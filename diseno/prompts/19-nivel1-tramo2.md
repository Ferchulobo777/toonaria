# 19 — Nivel 1, tramo 2: la plaza del reloj roto (NUEVO — pendiente)

**Guardar como**: `arte/nivel1-tramo2.jpg`.

**Por qué hace falta ahora**: el nivel 1 se extendió con cámara y scroll (revisión 2026-09-02,
ver GDD) — 5120px de largo en vez de 1280 fijos. Hoy los 4 tramos usan la MISMA imagen
(`nivel1-barrio-reloj.jpg`) repetida como placeholder, y eso no puede quedar así: el recorrido
tiene que seguir mostrando la ciudad, con calles y edificios distintos, no la misma cuadra cuatro
veces. Este es el segundo tramo (el jugador ya cruzó el primer pozo) — un paso más cerca del
centro de Toonaria, un poco más corrompido que el tramo 1.

**Cómo generarlo**: adjuntar `nivel1-barrio-reloj.jpg` (tramo 1, ya aprobado) como referencia de
estilo/paleta, para que se note que es la misma ciudad continuando, no un lugar sin relación.

```
Wide environment concept art, 1930s rubber-hose cartoon style (crisp
black ink lineart, mostly black and white with limited color accents,
warm amber gas-lamp glow), continuing the same foggy Victorian
clock-tower district from the attached reference — same art style and
palette, a different street within it: a small plaza with a large
ornate public clock fountain at its center, its clock face cracked and
showing an impossible hour. Clockmaker shopfronts continue along the
sides. A little more silvery moonlight corruption creeping in than
before — a couple of shop windows now reflect a full moon that isn't
in the sky, one lamppost bent at an unnatural angle like it's
straining away from the light. Side-view game-background composition
for a 2D platformer level, layered foreground/midground/background,
no characters in frame.
```

## Después de generarla

Reemplaza el tramo 2 (x 1280 a 2560) del fondo tileado placeholder en `game.json` — mismo
proceso que el resto: recortar/ajustar a 1280x720 si hace falta y pedirme que la importe.
