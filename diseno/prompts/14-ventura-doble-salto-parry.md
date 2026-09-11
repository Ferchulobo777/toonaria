# 14 — Ventura: doble salto y esquiva/parry (NUEVO — pendiente)

**Guardar como**: `arte/ventura-hoja-doble-salto-parry.jpg`, después recortar en poses
individuales igual que se hizo con `mov.jpg` (ver `arte/ventura-sprites/`).

**Por qué hace falta ahora**: la revisión del 2026-09-02 del GDD suma dos movimientos nuevos al
jugador — doble salto (para esquivar el Aullido del jefe saltando por encima) y esquiva/parry
(para devolver los proyectiles de Garra de luna, ver prompt 15). Ninguna de las 11 poses ya
recortadas de Ventura cubre esto: "Salto-Aire" es la caída/apex del salto simple, no sirve para
mostrar un segundo salto en el aire, y "Recibir Daño" es una reacción de dolor, no un gesto de
bloqueo/contraataque activo.

**Cómo generarlo**: adjuntar `ventura.jpg` (la referencia ya aprobada, cara rediseñada) como
imagen de referencia junto con este prompt, para mantener el mismo diseño.

```
Using the attached reference image of the character exactly as
designed (same face, hat, outfit, colors, proportions — do not
redesign the character), create a character pose reference sheet with
2 side-by-side full-body poses of the SAME character, 1930s
rubber-hose cartoon style, flat mid-gray background, consistent scale
across both poses:

1. Double jump — mid-air tumbling pose, body curled into a tight spin
   (like a somersault), coat tails and cape whipping around with the
   motion, a faint motion-blur arc behind him showing the spin
   direction. Reads clearly as a SECOND jump in the air, not a normal
   fall.
2. Parry/deflect — a sharp, confident counter stance: one arm swept
   out in front holding a card edge-on like a small shield/blade,
   weight braced low, a thin bright flash/glint at the point of the
   card as if it just struck something. Should read as an active,
   deliberate counter — not a pained flinch.

Label each pose faintly underneath (Doble Salto, Parry). Clean flat
cel-shaded coloring, character reference sheet style.
```

## Después de generarla

Mismo proceso que con `mov.jpg`: recortar cada pose (fondo plano, puedo automatizarlo con
Python/PIL como las veces anteriores) y guardarlas en `arte/ventura-sprites/` como
`doble_salto.png` y `parry.png` — quedan listas para importar como animaciones nuevas del
objeto `Player` en GDevelop (`SaltoDoble`, `Parry`).
