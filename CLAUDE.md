# Multimedia y Juegos en Web — Proyecto Integrador

Contexto para trabajar en este repositorio con asistencia de IA. Leer antes de tocar el
proyecto.

## La materia

Tecnicatura Universitaria en Desarrollo Web · FCAD · UNER. Asignatura **Multimedia y Juegos en
Web**, cursada 2026. Prof. titular: Lic. Fabián Marcelo Pineda · JTP: Tec. Univ. Hernán Ignacio
Hernández, Prog. Juan Ignacio Carubia Grieco.

Se trabaja con motores de juego web **por eventos/no-code**: **GDevelop** o **Construct 3**
(unidad 5 del programa). **Motor elegido: GDevelop** (2026-08-25) — gratis, open-source,
exportación sin costo a web/Android/desktop. Comparativa completa en el vault
(`06 Unidad 5 - Construccion con HTML5/Unidad-5-Index.md`).

La teoría completa de la cursada está documentada en un vault de Obsidian aparte (no en este
repo): `Boveda - Obsidian/Fernando/Tecnicatura Desarrollo Web/Multimedia y Juegos en Web`. Ese
vault tiene el detalle de cada unidad; acá sólo va lo necesario para diseñar/programar el juego.

## Cómo se aprueba (por qué importa para el proyecto)

Camino corto = parcial aprobado + **trabajo integrador** aprobado (promoción directa, sin
final). El trabajo integrador se defiende oralmente: el estudiante tiene que poder explicar
cada decisión de diseño y cada bloque de lógica que entrega. Esto condiciona cómo se documenta
y se comenta el proyecto acá — ver regla abajo.

## Regla de documentación/comentarios — IMPORTANTE

GDevelop y Construct 3 son motores de **lógica visual por eventos** (condición → acción), no de
código imperativo tradicional — la mayor parte del "código" son event sheets, no archivos de
texto. Aun así, la misma regla de fondo del resto de la carrera aplica acá:

- **Todo razonamiento tiene que poder explicarse en primera persona en la defensa.** Nunca se
  documenta ni se comenta nada como si lo hubiera decidido una IA — nada de "agregado para
  resolver X", "fix:", ni referencias a esta conversación, a un prompt o a que el diseño lo
  generó un asistente.
- **En los event sheets**: usar los bloques de comentario/anotación nativos de cada motor para
  anclar el *porqué* de una estructura de eventos no obvia (por qué un sub-evento, por qué esa
  condición y no otra), no para narrar qué hace el evento — el nombre del objeto/variable ya
  debería decir eso.
- **Cuando se use el modo avanzado** (bloques de JavaScript dentro de un evento, en cualquiera
  de los dos motores): mismo criterio que en cualquier código — comentarios en castellano, tono
  académico, comentar el porqué no el qué, sin sobre-explicar lo autoexplicativo.
- **Documentos de diseño (GDD, fichas de personaje, specs de nivel)**: se redactan como si los
  escribiera el estudiante documentando sus propias decisiones — la skill instalada (ver abajo)
  ayuda a producirlos, pero el criterio final y la justificación de cada elección tienen que
  poder sostenerse de palabra en la defensa.

## Convenciones del proyecto

- Nombres de objetos, variables, grupos de eventos y escenas en **castellano**, salvo términos
  técnicos estándar del motor (`sprite`, `behavior`/comportamiento, `event sheet`, `hitbox`,
  `cooldown` — se usan en inglés porque así se usan en la práctica de la industria).
  Criterio calcado del vault de teoría.
- Un **vertical slice jugable primero**, después expandir — evitar sobre-diseñar (10
  habilidades, 8 jefes, 12 niveles) antes de tener un ciclo core divertido y terminado. Ver
  `references/production-workflow.md` de la skill.
- Diseño antes que herramienta: no saltar a "poné este evento" sin antes tener claro qué
  experiencia se busca — un sistema sin propósito de diseño es solo un menú de números.

## Herramientas de IA disponibles en este proyecto

**Skill instalada** (`.agents/skills/gamedev-gdevelop-construct/`, a nivel de proyecto) — se
carga sola cuando la tarea la amerita, no hace falta invocarla a mano. Es una skill preparada
específicamente para esta materia, con 9 referencias:

| Capa | Referencia |
|---|---|
| Diseño / concepto | `game-design-fundamentals.md` |
| Narrativa | `narrative-and-writing.md` |
| Niveles | `level-design.md` |
| Arte y animación (incluye pixel art) | `art-and-animation.md` |
| Combate, habilidades, jefes | `combat-abilities-bosses.md` |
| Audio y game feel | `audio-juice-polish.md` |
| Implementación en GDevelop | `gdevelop-engine.md` |
| Implementación en Construct 3 | `construct-engine.md` |
| Producción / flujo de trabajo | `production-workflow.md` |

Se investigó si existían skills dedicadas a GDevelop o Construct 3 en repositorios/marketplaces
públicos (a diferencia de Godot, Unity, Unreal, Phaser, que sí tienen skills propias) y no se
encontró ninguna — esta fue, hasta donde se pudo comprobar, la única específica para ambos
motores, así que se armó desde cero. Se descartaron skills genéricas de pixel art de terceros
por reputación/mantenimiento desparejos frente a lo que ya cubre `art-and-animation.md`.

**Otras dos skills instaladas a nivel de proyecto (2026-09-02)**, complementarias a la de
arriba — esa es sobre criterio de diseño, estas son referencia técnica de qué existe realmente
en el motor:

- **`gdevelop-official-docs`** (`.agents/skills/gdevelop-official-docs/`) — resumen técnico de
  toda la wiki oficial de GDevelop 5 (`wiki.gdevelop.io/gdevelop5/`), en 5 archivos de
  referencia: objetos y comportamientos, eventos y expresiones, interfaz del editor, features
  core/extendidas, y publicación. Se carga sola cuando la duda es sobre el comportamiento real y
  documentado del motor (nombre exacto de una acción/condición, propiedades de un behavior) en
  vez de inferirlo. Ya se usó para una auditoría completa del proyecto (ver
  `diseno/GDD.md`, entrada del 2026-09-02) que encontró y limpió un bloque de eventos/objetos
  muertos en `Level1` (restos de una versión temprana del jefe, antes de que existiera la
  escena `ArenaJefe`).
- **`gdevelop-games-dashboard`** (`.agents/skills/gdevelop-games-dashboard/`) — gestión
  post-publicación de un juego en gd.games (analíticas de sesiones/retención, feedback de
  jugadores, administración de leaderboards, lobbies multijugador, exportaciones, Boosts de
  marketing). Sólo relevante una vez que haya una build publicada — hoy el proyecto todavía no
  llegó a esa etapa.

Ambas se instalaron con el CLI `skills` (mismo que gestiona la skill de arriba) y quedaron
registradas en `skills-lock.json`, en la raíz del repo.

**MCP y CLI de GDevelop — instalados a nivel de proyecto (2026-08-28).** GDevelop en sí ya
estaba instalado localmente (`C:\Program Files\GDevelop`). Se investigó qué herramientas de
automatización/agente existen para GDevelop (no hay CLI oficial del equipo de GDevelop, pero sí
dos proyectos de la comunidad, ambos de código abierto) y se dejaron listas para usar:

- **[`gdevelop-mcp`](https://github.com/gb2b/gdevelop-mcp)** (MIT, clonado y compilado en
  `.tools/gdevelop-mcp/`, no versionado — ver `.gitignore`). Servidor MCP con **30 herramientas**
  en 10 categorías: scaffolding de proyecto nuevo (`quick_start_template`: blank/platformer/
  topdown/shmup), introspección y búsqueda del proyecto, catálogo de ~1.830 acciones/condiciones/
  expresiones del motor, edición del proyecto con guardas de seguridad, acceso al asset store
  oficial (11.000+ items), 281 ejemplos oficiales MIT, y preview estático/runtime de escenas.
  Ya conectado vía `.mcp.json` en la raíz del proyecto (apunta a
  `.tools/gdevelop-mcp/dist/index.js`) — las herramientas aparecen como `mcp__gdevelop__*` y trae
  5 prompts/slash-commands propios. No hace falta tener un proyecto GDevelop creado para
  empezar: el propio MCP puede scaffoldear uno.
- **[`gdexporter`](https://www.npmjs.com/package/gdexporter)** (MIT, CLI de la comunidad para
  exportar un proyecto GDevelop sin abrir el editor — pensado para CI). Instalado como
  devDependency en el `package.json` de la raíz (`npm install` ya corrido) — se usa con
  `npx gdexport --project ./juego/game.json --out ./exports --build electron` (o sin `--build`
  para exportar a HTML5). También quedó disponible el binario dentro de
  `.tools/gdevelop-mcp/node_modules/.bin/`, porque `gdevelop-mcp` lo trae como dependencia
  propia.

**Para reconstruir la tooling en otra máquina** (no se versiona por tamaño — Puppeteer descarga
~170MB de Chromium):
```
git clone https://github.com/gb2b/gdevelop-mcp .tools/gdevelop-mcp
cd .tools/gdevelop-mcp && corepack enable pnpm && pnpm install && pnpm build
cd ../.. && npm install
```

## Documentación de diseño disponible

El vault de teoría ya tiene, listos para reutilizar al escribir el GDD del trabajo integrador
(`Multimedia y Juegos en Web/04 Unidad 3 - Documentos de Diseno/Unidad-3-Index.md`):
- La **plantilla de GDD completa de la cátedra** (40 secciones, de objetivos del juego a
  apéndice de scripts de voz).
- Dos **GDD reales de la industria** como referencia de nivel de detalle: *Torin's Passage*
  (Al Lowe/Sierra, 1995 — aventura narrativa) y el *Race'n'Chase* original de DMA Design (1995,
  el germen de *GTA* — sistemas, modos de juego, presupuesto técnico).
- El **monomito de Joseph Campbell** y la estructura narrativa de 3 actos
  (`03 Unidad 2 - Diseno de Videojuegos/Unidad-2-Index.md`), útiles si el juego tiene guión o
  progresión narrativa entre niveles.

## Estado del proyecto

**Motor: GDevelop** (decidido 2026-08-25). Requerimiento adelantado verbalmente por la cátedra
para el integrador: **3 niveles + 1 jefe final** (consigna escrita todavía no publicada).
Repositorio Git local inicializado (todavía sin remoto en GitHub). GDevelop, `gdevelop-mcp` y
`gdexporter` instalados y verificados (2026-08-28) — falta crear el proyecto `.json` de
GDevelop en sí. Se actualiza esta sección a medida que:
- Se decide el género/concepto del juego (en curso — ver conversación de diseño).
- Se conoce el enunciado escrito del trabajo integrador.
- Se arma el equipo (si lo hay) y el repositorio remoto en GitHub.
- Se crea el proyecto GDevelop y arranca el vertical slice.
- Avanza el desarrollo, unidad por unidad, en paralelo con la cursada.
