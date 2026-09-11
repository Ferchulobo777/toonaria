# Toonaria

Trabajo integrador de la asignatura **Multimedia y Juegos en Web** — Tecnicatura Universitaria
en Desarrollo Web, FCAD, UNER.

Plataformero de acción 2D hecho en **GDevelop 5**, ambientado en una ciudad victoriana dibujada
en blanco y negro estilo cartoon clásico (rubber-hose). El jugador controla a **Ventura**, un
cartomante que recorre la ciudad enfrentando al "Repintado" — un fenómeno que corrompe a los
habitantes que miran la luna llena de más — hasta el enfrentamiento final contra Ambrosio, su
mentor transformado.

## Estructura del repositorio

```
juego/            Proyecto GDevelop (game.json + assets). Se abre directo con el editor.
diseno/           Documentación de diseño:
  GDD.md          Documento de diseño del juego — historia, mecánicas, niveles, jefes,
                  bitácora de bugs y decisiones tomadas durante el desarrollo.
  arte/           Concept art, hojas de referencia de sprites, y la ficha de personaje
                  en pixel art (entrega de la unidad de Diseño Pixel Art).
CLAUDE.md         Contexto de la materia y convenciones del proyecto.
```

## Cómo abrir el proyecto

1. Instalar [GDevelop 5](https://gdevelop.io/) (gratis).
2. Abrir `juego/game.json` desde el editor (`Abrir un proyecto` → seleccionar el archivo).
3. La documentación de diseño completa está en `diseno/GDD.md` — leerla antes de tocar
   mecánicas o niveles para no pisar decisiones ya tomadas y justificadas.

## Convenciones del proyecto

- Nombres de objetos, variables, grupos de eventos y escenas en **castellano**, salvo términos
  técnicos estándar del motor (`sprite`, `behavior`, `hitbox`, `cooldown`).
- Comentarios de event sheets: explican el *porqué* de una estructura no obvia, no narran qué
  hace el evento.
- Cada decisión de diseño y cada bug encontrado durante el desarrollo queda registrado en
  `diseno/GDD.md` con la fecha — es el historial de decisiones del proyecto.

Detalle completo de reglas y criterio de diseño en `CLAUDE.md`.

## Estado

Ver `diseno/GDD.md` → sección "Pendientes abiertos" para lo que falta (niveles 2 y 3, sonido,
export real probado, etc.) y la bitácora de decisiones/bugs resueltos a lo largo del desarrollo.
