# Toonaria

![Pantalla de título](diseno/capturas/titulo.png)

**Plataformero de acción 2D en pixel art hecho en GDevelop 5.** Trabajo integrador de la
asignatura *Multimedia y Juegos en Web* — Tecnicatura Universitaria en Desarrollo Web, Facultad de
Ciencias de la Administración, Universidad Nacional de Entre Ríos (2026).

En Toonaria, una ciudad victoriana dibujada como un cartoon de los años 30, la luna llena
"repinta" a quienes la miran de más y los convierte en monstruos. **Ventura**, un cartomante que
pelea con cartas que se cargan, cruza la ciudad para encontrar a **Ambrosio**, el farolero que le
enseñó el oficio y que ahora es un lobo en la cima de la torre del reloj.

**Equipo**: Fernando Rubén Bareiro Ruiz · Mateo Fernández · Natalia Ailén González · Fernando
Rodríguez.

# Enlace directo al juego

* https://udw-grupo11.itch.io/toonariav2 


---

## Contenido

- **Prólogo jugable** que funciona de tutorial: un recuerdo en la carpa de Ambrosio, donde cada
  estación enseña una acción.
- **Tres niveles** —Barrio del Reloj, Barrio de los Teatros y Corazón de Toonaria—, cada uno con
  enemigos y obstáculos nuevos que después se combinan con los anteriores.
- **Jefe final de dos fases** con ciclos de ataques que se aprenden y un parry que devuelve sus
  proyectiles.
- **Cuatro tipos de enemigo** (Repintado, Actor, Cuervo y Agente), cada uno con un aviso visual y
  sonoro propio antes de atacar.
- Diálogos con retratos, epílogo y créditos, menú de capítulos, música y efectos de sonido
  propios.

| | |
|---|---|
| ![Prólogo: la carpa de Ambrosio](diseno/capturas/prologo.png) | ![Nivel 1: Barrio del Reloj](diseno/capturas/nivel1.png) |
| *Prólogo — la carpa de Ambrosio* | *Nivel 1 — Barrio del Reloj* |
| ![Nivel 2: Barrio de los Teatros](diseno/capturas/nivel2.png) | ![Nivel 3: Corazón de Toonaria](diseno/capturas/nivel3.png) |
| *Nivel 2 — Barrio de los Teatros* | *Nivel 3 — El Corazón de Toonaria* |
| ![Jefe final](diseno/capturas/jefe.png) | ![Créditos](diseno/capturas/creditos.png) |
| *La cima de la torre — Ambrosio* | *Créditos* |

![Fase 2 del jefe: garras de luna, aullido y embestida](diseno/capturas/jefe-fase2.gif)

## Cómo jugar

| Acción | Teclas |
|---|---|
| Moverse | Flechas o A / D |
| Saltar (doble salto en el aire) | Espacio o W — mantener para saltar más alto |
| Carta lunar | Mantener X o J para cargar, soltar para tirar |
| Farol incendiario | C o K |
| Parry (devuelve proyectiles) | Z o L, justo antes del golpe |
| Pasar diálogo | Enter |
| Pausa | Esc |

Desde el título, **Capítulos** lleva directo a cualquier nivel o al jefe.

### Abrir el proyecto

1. Instalar [GDevelop 5](https://gdevelop.io/).
2. Abrir `juego/game.json` (*Abrir un proyecto*) y usar *Vista previa*.

### Exportar a web

Requiere [Node.js](https://nodejs.org/). Una sola vez, en la raíz del repositorio:

```bash
npm install
```

Después:

```bash
npx gdexport --project ./juego/game.json --out ./exports/web
```

La carpeta `exports/web` se sirve con cualquier servidor estático o se comprime en un ZIP para
subirla a itch.io como juego HTML5.

## Estructura del repositorio

```
juego/                    Proyecto GDevelop
  game.json               Escenas, objetos y eventos
  assets/pixel/           Sprites, fondos, tiles, efectos y HUD en pixel art
  assets/sonido/          Efectos de sonido
  assets/musica/          Temas musicales
diseno/
  GDD.md                  Documento de diseño (plantilla de la cátedra) y bitácora
  Guion.md                Guion y diálogos del juego
  Ficha-Personaje-Ventura.md
  arte/personajes/        Arte conceptual de personajes
  arte/escenarios/        Ilustraciones de cada barrio (base de los fondos)
  arte/logo/              Logo del juego
  arte/pipeline/          Scripts que convierten el arte en pixel art del juego
  audio/                  Síntesis de los efectos de sonido y la música
  capturas/               Capturas del juego
herramientas/
  construir_juego.py      Genera juego/game.json: objetos, eventos, escenas y niveles
  validar_eventos.mjs     Controla cada condición y acción contra el motor
  validar_expresiones.mjs Controla cada expresión con el validador del motor
  probar_juego.mjs        Juega la exportación con teclas reales y registra el estado
entregas/entrega-1/       Primera entrega (29-9)
```

## Cómo se construye

El juego se genera desde scripts para que todo sea reproducible y cada cambio se pueda revisar en
Git. Requisitos: Python 3 con `numpy`, `scipy` y `Pillow`, Node.js y `ffmpeg` (sólo para la
música).

Generar y validar el proyecto:

```bash
python herramientas/construir_juego.py
```

```bash
node herramientas/validar_eventos.mjs juego/game.json
```

```bash
node herramientas/validar_expresiones.mjs juego/game.json
```

El exportador de GDevelop descarta en silencio las instrucciones inválidas (el juego compila, pero
ese evento nunca hace nada), por eso cada instrucción se valida contra el motor antes de exportar.

Pruebas automáticas con teclado real (instalar `puppeteer` aparte, no es dependencia del
proyecto):

```bash
npm install --no-save puppeteer
```

```bash
node herramientas/probar_juego.mjs exports/web escenario.json salida/
```

Si se edita el proyecto en el editor de GDevelop, el cambio tiene que pasarse a
`herramientas/construir_juego.py`: regenerar `game.json` sobrescribe el archivo.

## Documentación

- [Documento de diseño (GDD)](diseno/GDD.md): mecánicas con sus números, enemigos, niveles, jefe,
  arte, sonido, implementación y la bitácora de decisiones.
- [Guion](diseno/Guion.md): la historia escena por escena y todos los diálogos del juego.
- [Ficha de personaje](diseno/Ficha-Personaje-Ventura.md).

## Licencia

GPLv3 — ver [`LICENSE`](LICENSE).
