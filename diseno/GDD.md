# Game Design Document — Toonaria

Estructura basada en la plantilla de la cátedra (ver
`Multimedia y Juegos en Web/04 Unidad 3 - Documentos de Diseno/Unidad-3-Index.md` en el vault).
Documento vivo: se va completando a medida que el diseño se cierra — no hace falta llenar todo
antes de prototipar (ver ciclo de prototipado en la Unidad 2 del vault).

Versión del documento: 0.3 — 2026-09-02.

---

## Objetivos del juego

**Gran concepto**: un plataformero de acción con estética "Bloodborne, pero toon" —
ambientación gótico-victoriana (farol, levita, niebla) resuelta con un estilo de animación
cartoon clásico (rubber-hose), en vez del tono realista/sombrío del referente. El combate es a
distancia, no cuerpo a cuerpo como en Bloodborne — el jugador carga y arroja cartas.

**Reverso de la caja / qué lo hace distinto**: un shooter de plataformas con un arma "de mazo"
(cartas) en vez de balas o magia genérica, con mecánica de carga que recompensa el timing en
vez de spamear el ataque.

## Descripción general de la historia

> [!info] Inventada a pedido — v1, todo abierto a cambios
> Primera pasada narrativa, para darle marco a los 3 niveles + jefe y a los elementos que ya
> estaban definidos (farol, cartas con símbolo de luna, jefe lobo). Nombres y detalles son
> propuesta, no definitivo.

**Configuración**: Toonaria es una **ciudad enorme**, victoriana antigua y oscura — pero
dibujada enteramente en blanco y negro estilo cartoon clásico (rubber-hose): callejones de
tinta, adoquines de cuadrícula, faroles de gas en cada esquina, niebla que no deja ver los
edificios más altos. Cada tanto sale **luna llena de tinta plateada**: esa noche, la luz de la
luna se filtra por las rendijas del papel del mundo y "sobre-tiñe" a los habitantes que la
miran de más, borrándoles la identidad y dejando en su lugar una versión monstruosa, feral, de
sí mismos. La ciudad le llama **el Repintado**, y ya lleva varias lunas extendiéndose barrio
por barrio — cada vez alcanza a más gente, cada vez está más cerca del corazón de la ciudad.

**Protagonista — propuesta de nombre: "Buenaventura" (le dicen "Ventura")**: cartomante de uno
de los barrios más viejos de Toonaria — lee la suerte con un mazo de cartas moradas marcadas
con símbolos de luna, y esas mismas cartas, cargadas, son su forma de pelear. Antes de la
historia, ese mazo era solo para adivinar; el Repintado lo obliga a usarlo para algo más. De
toda la ciudad, es el único que no le teme a mirar la luna de frente sin transformarse —
nadie sabe bien por qué, ni siquiera él — y por eso es el único que puede recorrer Toonaria de
punta a punta sin correr el riesgo de convertirse él mismo en lo que está cazando.

**El farol**: perteneció a **Ambrosio, el Farolero** — el toon encargado de encender los
faroles de gas de todo el barrio de Ventura cada noche, mentor/amigo cercano suyo, quien le
regaló el farol antes de todo esto. Ambrosio fue el primer Repintado que se conoció en la
ciudad: la noche que se quedó mirando la luna llena de más, demasiado tiempo, se transformó en
un **lobo toon** y desapareció hacia el centro de Toonaria. Ventura conserva su farol, pero no
lo lleva encima todo el tiempo — es un recordatorio, no un arma, y de ahí sale la animación de
espera (guardarlo, o tirar una moneda mientras lo piensa dos veces antes de salir a buscarlo).

**El plot**: Ventura recorre Toonaria, barrio por barrio, hacia el centro de la ciudad —
siguiendo el rastro de Ambrosio y tratando de frenar al Repintado antes de que se trague a toda
la ciudad en la próxima luna llena. Cada uno de los 3 niveles es un barrio distinto, cada vez
más cerca del centro y cada vez con el Repintado más fuerte (enemigos cada vez más "corridos de
tinta"). El jefe final, al llegar al corazón de Toonaria, es Ambrosio ya completamente
transformado — Ventura tiene que elegir entre pelear para "revertirlo" o aceptar que ya no
puede.

**Final (propuesta, abierta)**: derrotar al jefe apaga el Repintado en él (vuelve a su forma
toon, aunque no se explicita si "vuelve a ser el mismo") — deja abierta una continuación (no
hace falta resolverlo del todo para el alcance del entregable, ni explicar todavía por qué
Ventura es inmune a la luna).

## Controles del juego

> [!warning] Revisión 2026-09-02 — se amplía el kit de movimiento
> El punto 11 de "Pendientes abiertos" había descartado agacharse y doble salto para el alcance
> del entregable. Se revisa esa decisión: la pelea contra Ambrosio se diseñó con un ataque a
> distancia (Aullido, onda expansiva) y necesita que el jugador tenga con qué responder más
> allá de correr — doble salto para escapar verticalmente de una onda expansiva grande, y una
> esquiva/parry para el nuevo ataque de proyectiles del lobo (ver Jefes). No es sumar movimiento
> porque sí: cada movimiento nuevo responde a un ataque puntual del jefe, mismo criterio de
> "no diseñar en el vacío" del `CLAUDE.md`.

- Movimiento horizontal + salto (comportamiento de Plataformas de GDevelop).
- **Doble salto**: un segundo salto en el aire — pensado para esquivar verticalmente el Aullido
  del jefe (onda expansiva que conviene saltar por encima) sin depender del timing exacto de un
  salto simple.
- **Parry** (tecla `Z`): ventana de 0.25s — si el proyectil `GarraLuna` del jefe conecta durante
  esa ventana, se destruye y le devuelve 25 de daño al jefe en vez de pegarle a Ventura (ver
  "Ataque de proyectiles" en Jefes) — estilo Cuphead: parry como herramienta de combate, no solo
  defensa pasiva. **Implementado y verificado** (2026-09-02) — a propósito, solo protege contra
  proyectiles, no contra los ataques de contacto del jefe (Embestida/Zarpazo/Aullido siguen
  pegando igual); no tiene cooldown entre usos todavía, se puede spamear sin costo.
- Cargar carta (mantener) → soltar para arrojar.
- Farol-bomba (botón separado, sin carga — ver arma secundaria).

**Pendiente de arte**: doble salto y parry necesitan poses nuevas de Ventura (giro en el aire,
gesto de parry) que todavía no existen en `diseno/arte/ventura-sprites/` — hay que generarlas
antes de poder implementar la animación (la lógica de GDevelop puede armarse en paralelo con un
placeholder, pero no queda lista "de verdad" hasta tener el sprite).

## Personaje del jugador

**Nombre (propuesta): Buenaventura, "Ventura"** — cartomante del pueblo de Toonaria, ver
historia arriba.

**Apariencia**: figura estilo cartoon clásico (rubber-hose, blanco y negro con acentos de
color), con vestuario gótico-victoriano — levita, moño, capa, botas de dos tonos.

> [!warning] Pendiente de resolver — parecido con Bendy
> El diseño de cabeza del concept art de referencia (orejas curvas tipo cuerno, ojos de botón
> negros, sonrisa enorme) es muy cercano al personaje **Bendy** (*Bendy and the Ink Machine*,
> Joey Drew Studios) — no es una influencia estilística genérica del rubber-hose, es
> reconocible como ESE personaje puntual. Para poder defender el diseño como propio en el
> integrador, y para no tener problemas si el juego se publica en algún sitio, hay que
> rediseñar específicamente la cabeza/cara antes de pasar a sprites finales. El resto del
> concept (vestuario gótico-victoriano, paleta, silueta del cuerpo) no tiene ese problema.
>
> **Prompt listo para resolverlo** (2026-09-02): `diseno/arte/prompt-plantilla-ventura.md` —
> pide de una la cabeza rediseñada (ojos expresivos con iris, sonrisa cerrada tipo showman,
> bigote fino como rasgo distintivo, sin orejas visibles) Y una sola hoja con las **14**
> animaciones que usa el personaje (espaciado real entre sí, causa de fondo del problema de
> sprites "sucios" de la tanda anterior — era la plantilla `mov.jpg`, no el método de recorte,
> ver entrada de auditoría más abajo). Ojo: no son 11 poses + las otras 3 aparte — las 14 van
> juntas en el mismo prompt para que salgan con la misma cara de una — el personaje sólo mira
> hacia la derecha en todo el arte, el motor lo espeja con `FlipX` para el otro lado (ya
> implementado), así que ninguna pose necesita versión "mirando para atrás" ni "girando" propia
> — se evaluó explícitamente duplicar a 28 poses (izquierda y derecha) y se descartó, `FlipX`
> ya está probado y andando en el proyecto.
>
> **Primer intento fallido** (2026-09-02): el generador de imágenes ignoró dos instrucciones del
> prompt — metió texto (título y una leyenda debajo de cada pose) y devolvió una hoja de
> personaje genérica (sitting, bowing, tipping hat, expression sheet) en vez de las 14 poses
> pedidas. El prompt quedó reforzado (regla de "sin texto" repetida al principio y al final,
> chequeo final explícito de las 14 poses) — detalle en el propio archivo. Todavía sin generar
> con el prompt reforzado ni aplicado al proyecto.

**Farol**: es un prop situacional, no parte fija de la silueta — el personaje no lo lleva
puesto/en mano todo el tiempo. Posible uso: animación de idle (guardarlo, o tirar una moneda al
aire como gesto de personalidad) — a definir cuál queda como "tell" de espera del personaje.

## Habilidades del jugador — arma principal: cartas

- **Cartas moradas con símbolo de luna** — arma a distancia principal (y por ahora única).
- **Mecánica de carga**: el jugador mantiene presionado el botón de ataque, una barra de carga
  se llena; al soltar, arroja la carta. Inspiración de mecánica: Gambit (X-Men) — cargar un
  objeto y arrojarlo para que explote (esto es una referencia de *mecánica*, no de diseño
  visual — no genera el mismo problema que el punto anterior).
- **Explosión**: la carta explota al impactar (¿o tras un tiempo fijo, tipo granada? — a
  definir) — probablemente el radio/daño de la explosión escale con cuánto se cargó el tiro.
- **Tope de carga para el entregable**: la barra tiene un máximo fijo (no infinito) — al llegar
  al tope, se queda ahí hasta soltar, no sigue subiendo/no hay sobrecarga con riesgo. Es un
  medidor por-tiro (se llena mientras se mantiene apretado, se vacía al soltar y arrojar), no un
  recurso limitado tipo "mazo de cartas" — así que no hay gasto que se agote, se puede cargar y
  tirar todas las veces que haga falta.
- **Escalado de daño**: soltar antes de llegar al máximo tira una **carta más débil**, con daño
  (¿y/o radio de explosión?) proporcional a cuánto se cargó — no es todo-o-nada. Implica más
  frames de animación de la carga (mínimo 2-3 etapas visuales: sin cargar/media carga/carga
  completa, para que el jugador vea en qué nivel está antes de soltar) y más trabajo de balance
  (definir la curva de daño por nivel de carga), pero da más profundidad táctica — se puede
  disparar rápido y débil para presionar, o arriesgarse a cargar a fondo para un golpe fuerte.
- **Progresión de la barra (fuera del alcance del entregable)**: subir el máximo de carga
  derrotando jefes o comprando mejoras en una tienda es un sistema de progresión de juego
  completo — no entra en el alcance de tutorial + 3 niveles + jefe final. Queda anotado como
  posible expansión post-entrega, no se implementa ahora.

## Vida

- **Barra de vida** — arriba a la izquierda (convención estándar, separada de las barras de
  recurso de ataque que van en el pie de pantalla). `Vida` / `VidaMax`, ambas variables del
  objeto Player. Fuentes de daño: todavía no hay enemigos implementados — la variable y la
  barra quedan listas para cuando se sumen.

## Maná y regeneración — revisión de la mecánica de carga

> [!warning] Revisión 2026-09-01
> En la primera versión de este documento se había definido que cargar/arrojar cartas **no**
> consumía ningún recurso limitado ("se puede cargar y tirar todas las veces que haga falta").
> Se decidió sumar maná como recurso — esta sección reemplaza esa parte.

- **Maná** (`Mana` / `ManaMax`, variables del Player): arrojar una carta consume maná. El costo
  escala con cuánto se cargó el tiro (mismo criterio que el daño) — una carta débil cuesta poco,
  una carga completa cuesta más. Si no hay maná suficiente para el costo calculado, se cobra
  solo el maná disponible (tiro débil igual, no se bloquea del todo salvo con maná en 0).
- **Regeneración con demora**: el maná no se recupera mientras se lo esté gastando activamente —
  recién empieza a regenerarse solo después de un tiempo fijo sin usar ningún ataque
  (`ManaRegenDelay`), y ahí sube de a poco (`ManaRegenRate` por segundo) hasta el tope. Esto
  evita que el jugador spamee cartas sin parar — tiene que administrar cuándo cargar a fondo y
  cuándo parar a dejar que se recupere.

## Farol incendiario — arma secundaria

- **Segunda arma**: además de las cartas, Ventura puede arrojar el farol como una bomba
  incendiaria — tiene sentido con la historia (el farol es de Ambrosio, el farolero) y con la
  Unidad 2 del vault (variar el kit de combate sin duplicar la mecánica de carga).
- A diferencia de la carta, **no se carga** — se tira directo con un botón separado, con un
  **arco simple** (velocidad vertical inicial + gravedad, no en línea recta) para que se sienta
  como un lob de verdad. Cuesta más maná que una carta (es más potente/de área) — a definir el
  valor exacto de daño de área en la próxima pasada de balance.
- Reutiliza la animación `Arrojar` del jugador por ahora (no hay pose específica dibujada para
  esta arma todavía) — el proyectil en sí usa un ícono placeholder generado
  (`assets/projectiles/farol_bomba.png`), a reemplazar cuando se dibuje el farol-bomba real (ver
  `Prompts-Arte/` para encargar ese prompt).
- **Pulido 2026-09-02**: la pose `Arrojar` ahora se sostiene ~0.35s después de cargar/soltar
  cualquiera de las dos armas (antes duraba un solo frame porque los eventos de Idle/Correr la
  pisaban al instante) — se implementó con una variable `TiempoArrojo` en vez del timer nativo
  de GDevelop, para no mezclar dos sistemas de tiempo distintos en el mismo proyecto.

## Sistema HUD

> [!warning] Revisión 2026-09-02 — reubicación de la barra de maná
> La barra de maná vivía en el footer junto a la de carga. Se movió arriba a la izquierda,
> apilada debajo de la de vida — vida y maná son los dos recursos "de supervivencia" del
> personaje y van juntos con la convención clásica de HUD; la de carga es distinta (un medidor
> de acción puntual, no un recurso que se agota) y se queda sola en el footer.

- **Barra de vida**: arriba a la izquierda, fija.
- **Barra de maná**: arriba a la izquierda, apilada justo debajo de la de vida, fija — ambas
  estáticas en pantalla, no siguen a nada.
- **Barra de carga**: barra horizontal fija en el pie de pantalla (footer), visible todo el
  tiempo. Se llena mientras se mantiene presionado el botón de ataque, hasta tocar el tope fijo.
- **Barras de vida de enemigos comunes** (`Repintado` y cualquier enemigo raso futuro): mini
  barra flotante que aparece arriba de la cabeza de cada enemigo y lo sigue en su patrulla — a
  diferencia de la del jugador, esta sí sigue al objeto. Se resuelve con la extensión nativa de
  GDevelop "Objetos vinculados" (LinkedObjects): cada enemigo nace ya vinculado a su propia
  barra, así que aunque haya varios en pantalla cada uno arrastra la suya y no la de al lado.
  Desaparece junto con el enemigo cuando muere.
- **Barra de vida del jefe**: grande, fija en el pie de pantalla (no flota sobre su cabeza como
  las de los enemigos comunes) — convención de jefe de Cuphead/Bloodborne: ocupa una franja
  claramente distinta a las del jugador, siempre visible mientras dura la pelea. Todavía no está
  implementada (el jefe no tiene instancia en ninguna escena) pero queda definido el criterio de
  diseño para cuando se arme la arena.
- Progreso de nivel, etc.: pendiente de definir.

## Jefes

**Ambrosio, el Farolero** — mentor de Ventura, transformado en lobo toon por el Repintado (ver
historia arriba y el guión completo en `Guion.md`). Es el único jefe del entregable (requisito
de cátedra: 1 jefe final — ver `08 Trabajo Integrador/Proyecto-Integrador.md` del vault).

### Diseño de combate — 2 fases

> [!success] Arte listo (2026-09-02)
> Las 5 poses del jefe (Guardia, Embestida, Zarpazo, Aullido, Transición) ya están generadas,
> recortadas e importadas al proyecto de GDevelop como el objeto `AmbrosioLobo` con sus
> animaciones nombradas — ver `diseno/arte/ambrosio-lobo-sprites/`. Todavía no tiene instancia
> en ninguna escena (falta armar la arena del jefe, ver Unidad 5) ni la lógica de IA de las 2
> fases — eso sigue pendiente.

Idea central: la pelea dramatiza la dualidad farolero/lobo del propio personaje — arranca
"metódico" (todavía queda algo de Ambrosio, el que enseñaba con orden) y termina errático (ya
domina el lobo). Referencia de telegraphing/patrones usada: Unidad 2 del vault y la skill de
proyecto (`combat-abilities-bosses.md`).

> [!warning] Revisión 2026-09-02 — pelea por patrones, no reactiva
> Se decide que el jefe no elige ataques al azar/según distancia del jugador (IA reactiva
> simple), sino que **repite un ciclo fijo de patrones**, igual que un jefe de Cuphead o de
> Bloodborne: el jugador puede aprenderse el orden y anticipar, en vez de improvisar cada vez.
> Cada fase tiene su propio ciclo (ver tablas de ataques de cada fase) — el orden dentro del
> ciclo es fijo, lo que cambia entre fases es qué ataques entran y cuánto dura el telegraph.

**Ataque de proyectiles (nuevo, fase 2)**: Ambrosio-lobo dispara garras de luz de luna —
visualmente son del mismo morado con símbolo de luna que las cartas de Ventura, no casualidad:
es la misma magia lunar, del lado corrupido. Se pueden **parryear** con la esquiva/parry nuevo
del jugador (ver Controles) — conectar el parry en la ventana justa devuelve el proyectil hacia
el jefe, estilo Cuphead. Es la pieza que le da sentido de diseño al parry: sin este ataque, la
esquiva sería solo un dash más.

**Fase 1 — "El Farolero" (100%-50% HP)**

| Ataque | Telegraph | Descripción | Cómo se esquiva |
|---|---|---|---|
| Embestida | Se agacha y gruñe (~1s) | Carga en línea recta hacia Ventura. | Saltar por encima, o moverse al costado — es la misma esquiva que enseña el circuito del prólogo/tutorial (guiño intencional). |
| Zarpazo | Levanta una garra, brillo de luna en las uñas | Golpe de melee de arco corto. | Mantener distancia — es de rango corto a propósito, para empujar al jugador a jugar a distancia con las cartas, que es la fortaleza del kit. |

**Ventana de castigo**: después de la Embestida, Ambrosio queda un instante enterrado/atascado
(recovery) — momento para cargar una carta a fondo sin apuro.

**Transición de fase (50% HP)**: Ambrosio parpadea un instante a su silueta humana —se le
escucha un quejido, casi su voz real— antes de que la luz de luna que entra por la ventana de
la torre lo cubra de nuevo, más fuerte. Cambio visual de arena: la luz de luna en escena se
vuelve más intensa/más cercana.

**Fase 2 — "El Lobo" (50%-0% HP)**

| Ataque | Telegraph | Descripción | Cómo se esquiva |
|---|---|---|---|
| Embestida | Igual que en fase 1, pero más corta (menos tiempo de reacción) | Igual que en fase 1, más rápida. | Igual, pero exige más precisión de timing. |
| Aullido | Se para en dos patas, aúlla | Onda expansiva de luz de luna que se expande desde su posición — ataque a distancia, obliga a moverse aunque el jugador esté jugando "de lejos" con las cartas. | Saltar por encima de la onda (doble salto si el timing no da con uno solo), o alejarse lo suficiente antes de que llegue. |
| Garra de luna | Junta las garras al pecho, brillo morado | Tira 2-3 proyectiles de luz de luna morada (mismo símbolo que las cartas de Ventura) en línea hacia el jugador. | Parry — devuelve el proyectil y le pega daño extra al jefe si conecta en la ventana justa; también se puede esquivar por debajo/costado sin arriesgar el parry. |

**Ciclo de fase 2**: Embestida → Garra de luna → Aullido → (repite). El orden es fijo para que
se pueda aprender; lo que varía con el HP restante es cuánto se acorta el telegraph de cada uno
(más cerca de 0 HP, menos tiempo de reacción — sin cambiar el orden del ciclo).

Con la Embestida repetida en ambas fases (más rápida en la 2), el Aullido y la Garra de luna
nuevos en la fase 2, alcanza para que la pelea se sienta distinta sin necesitar una tercera fase
— ítem a revisar en playtesting si se siente corta o repetitiva.

## Extensión del Nivel 1 (revisión 2026-09-02)

> [!warning] Decisión que reemplaza la anterior ("una sola pantalla")
> El nivel 1 estaba acotado a 1280px fijos porque el fondo se había generado para una sola
> pantalla, sin cámara. Se revierte: el nivel ahora es **estilo Cuphead** — largo, con cámara que
> sigue al jugador, más enemigos repartidos y obstáculos (pozos que exigen saltar). El "banco de
> pruebas" del jefe (`AmbrosioLobo` + su barra grande) se sacó de `Level1` — no tenía sentido que
> el primer nivel real comparta pantalla con un jefe de 200 HP. Toda su lógica de IA sigue
> intacta en el archivo (objeto, animaciones, los ~35 eventos de la máquina de estados), solo sin
> instancia en ninguna escena — no hace nada hasta que se le vuelva a poner una instancia en la
> arena final.

**Estructura actual** (5120px de largo, antes 1280):
- **Piso partido en 3 tramos** con 2 pozos de 200px entre ellos (x 1650-1850 y x 3300-3500) —
  hay que saltarlos, si se cae cuenta como golpe letal y reaparece por el sistema de
  muerte/respawn ya armado (mismo criterio que cualquier otro daño a 0 HP).
- **8 `Repintado`** repartidos a lo largo de todo el recorrido (antes 2, todos en la primera
  pantalla) — cada uno patrulla alrededor de su propia posición de spawn (±250px, ver nota
  técnica abajo), no todo el nivel.
- **Cámara con scroll**: sigue a Ventura, clampeada para no mostrar nunca más allá de los bordes
  del nivel.

> [!info] Nota técnica — patrulla de Repintado
> La patrulla usaba un rango fijo hardcodeado (x 60 a 1180) pensado para la pantalla única. Con
> el nivel extendido eso hacía que cualquier Repintado más allá de x=1180 caminara sin parar de
> vuelta hacia la pantalla 1. Se cambió para que cada instancia calcule su propio rango al
> arrancar la escena (su X inicial ±250), así cada uno se queda cuidando su tramo.

**Placeholder que hay que reemplazar — el fondo está TRIPLICADO, no es 3 tramos distintos**: los
4 paneles de fondo (0-1280, 1280-2560, 2560-3840, 3840-5120) hoy son la MISMA imagen
(`nivel1-barrio-reloj.jpg`) repetida 4 veces, solo para poder probar el scroll ya mismo. Pedido
explícito: el recorrido tiene que seguir mostrando la ciudad — plazas distintas, edificios
nuevos, cosas raras propias de este mundo toon corrompido por el Repintado — no la misma cuadra
cuatro veces. Quedan pedidos 3 paneles nuevos en `diseno/prompts/` (19, 20, 21) para reemplazar
los tramos 2, 3 y 4 (el tramo 1 se queda con el arte original, ya aprobado).

**Pendiente de ajuste una vez haya playtesting real** (esta tanda se armó y verificó
estructuralmente —sin errores en el motor— pero no hay forma de simular que alguien mueva a
Ventura con las teclas dentro de esta sesión, así que el balance de distancias/dificultad de los
pozos y el espaciado de enemigos está sin probar a mano):
- Si el salto normal/doble alcanza cómodo para cruzar los pozos de 200px, o hay que ajustar el
  ancho.
- Si 8 enemigos en 5120px se siente cargado o vacío.
- ~~Variedad de obstáculos: por ahora solo hay pozos~~ — **resuelto parcialmente**: se agregó
  `PlataformaMovil` (reutiliza la textura de piso, sin arte nueva), un segundo tipo de obstáculo.
  Vaivén fijo entre dos puntos (x 4500-4700) cruzando un tercer pozo de 300px — a diferencia de
  los otros dos, este no se puede saltar directo, exige subirse a la plataforma en movimiento.
  Sigue habiendo margen para más variedad (algo destructible con una carta, etc.) en una segunda
  pasada.

## Niveles del juego

Requisito de cátedra: **1 nivel tutorial + 3 niveles jugables + 1 jefe final**. Estructura y
temática ya definidas en `Guion.md`:

| Nivel | Barrio | Foco |
|---|---|---|
| Prólogo/tutorial | Carpa de Ambrosio (flashback) | Enseña controles en la ficción — no es un nivel "real" del recorrido actual. |
| Nivel 1 | Barrio del Reloj | Primer contacto con el Repintado — enemigos más asustados que agresivos. |
| Nivel 2 | Barrio de los Teatros | Sube la dificultad — primeros patrones de ataque coordinados. |
| Nivel 3 | El Corazón de Toonaria (plaza y torre del reloj central) | Máxima corrupción, lleva directo al jefe. |
| Jefe final | Cima de la torre del reloj | Ambrosio transformado. |

---

## Pendientes abiertos (para la próxima sesión de diseño)

1. ~~Rediseñar la cabeza/cara del personaje (separarse de Bendy)~~ — **resuelto y aprobado**:
   ver `diseno/arte/ventura.jpg` (generado a partir del prompt #1 de `Prompts-Arte.md`) —
   sombrero de ala ancha con dije de luna en vez de las orejas curvas, ojos con pupila/ceja,
   sonrisa contenida. También aprobados y en `diseno/arte/`: `ambrosio-farolero.jpg`,
   `ambrosio-lobo.jpg`, `carta-luna.jpg`, `repintado-generico.jpg`, `nivel1-barrio-reloj.jpg`,
   `nivel2-barrio-teatros.jpg`, `nivel3-corazon-toonaria.jpg`, `logo-toonaria.jpg` — **el kit
   completo de arte inicial (9/9) está listo**.

**Idea nueva, sin decidir — "Mr. Barnaby" como mini-jefe opcional**: el diseño del repintado
genérico (`repintado-generico.jpg`) salió con suficiente personalidad propia (hasta nombre en
el delantal) como para pensarlo como un segundo jefe, no solo enemigo de relleno. **No se
implementa ahora** — el requisito de cátedra es 1 jefe final y ya está diseñado el combate de
Ambrosio; sumar otro jefe implica otro set de ataques y otro sprite sheet de combate completo.
Se retoma solo si sobra tiempo después de tener el vertical slice completo (tutorial + 3
niveles + Ambrosio) andando — mismo criterio de "vertical slice primero" del `CLAUDE.md`.
2. ~~Nombre del juego~~ — resuelto: **Toonaria**. Nombre del personaje propuesto: Buenaventura
   ("Ventura") — confirmar o cambiar.
3. ~~Historia~~ — resuelta en `Guion.md` v0.2, abierta a ajustes.
4. ~~Cerrar la mecánica de carga~~ — resuelto: barra con tope fijo, sin recurso limitado, daño
   escalado (no todo-o-nada).
5. Explosión de la carta: ¿al impacto o por tiempo fijo (tipo granada)? — detalle de balance,
   no bloquea el arte.
6. ~~Diseño de combate del jefe~~ — resuelto: 2 fases (Farolero/Lobo), 3 ataques con
   telegraphing, ver arriba.
7. Resto del HUD (vida, progreso de nivel) — detalle, no bloquea el arte del personaje.
8. ~~Por qué Ventura es inmune a la luna~~ — resuelto en `Guion.md`: lee la luna reflejada en
   sus cartas, nunca la mira directo — es oficio, no destino.
9. Diálogo/letreros ambientales de nivel 1 y 2 — están los *beats*, falta el texto línea por
   línea (ver `Guion.md`) — no bloquea el arte.
10. ~~Producción de sprites de Ventura~~ — **resuelto**: 11 poses recortadas con fondo
    transparente en `diseno/arte/ventura-sprites/` (idle, carga1, carga2, carga_completa,
    correr, salto_inicio, salto_aire, aterrizaje, arrojar, recibir_dano, recuperacion) — listas
    para importar como frames de animación en GDevelop. Faltan solo Ambrosio (humano y lobo) y
    el repintado genérico, con el mismo proceso.
11. ~~Kit de movimiento — decidido, no agachar/no doble salto~~ — **revisado 2026-09-02**: se
    suma doble salto y esquiva/parry (ver Controles del juego), pedidos puntualmente por el
    ataque de Aullido y el nuevo ataque de proyectiles del jefe — no es la misma situación que
    cuando se descartó agacharse (que no respondía a ninguna necesidad concreta de combate).
    Agacharse se sigue descartando, sigue sin tener un ataque del jefe que lo requiera. Falta:
    sprites de las poses nuevas (giro de doble salto, gesto de parry) y toda la implementación
    en GDevelop — ver "Estado de implementación".

---

## Estado de implementación en GDevelop (`Proyecto/juego/game.json`)

> Esta sección trackea qué está *implementado y probado en el motor real* (no solo diseñado).
> Se actualiza a medida que se arma el proyecto — última actualización: 2026-09-02.

**Andando y verificado** (sin errores en `preview_scene`, motor real vía Chromium):
- Escena `Level1` (Barrio del Reloj) — fondo, suelo y paredes invisibles en los bordes
  ajustados al ancho real del arte (1280px, una sola pantalla — sin cámara con scroll porque el
  fondo no está pensado para eso todavía, ver Unidad 5 del vault).
- `Player`: 11 animaciones de Ventura, cambio de animación según estado (idle/correr/salto),
  flip por dirección.
- Carga y tiro de cartas (`Player` + objeto `Carta`), maná con regeneración demorada, HUD de
  vida/maná/carga con barras que reaccionan a las variables en tiempo real.
- Farol-bomba (`FarolBomba`) como arma secundaria, con arco simple (gravedad).
- Pose `Arrojar` sostenida ~0.35s (antes duraba 1 frame).
- **Enemigo `Repintado`**: patrulla de pared a pared, vida propia, recibe daño de `Carta` y
  `FarolBomba` (y se destruyen al pegar), muere a los 0 HP, devuelve daño de contacto a Ventura
  con 0.8s de invulnerabilidad para no derretirle la vida de un toque. **Barra de vida mini
  flotante** sobre la cabeza de cada instancia, vinculada por objeto (extensión LinkedObjects)
  así cada enemigo arrastra la suya y no la de otro — se borra sola cuando el enemigo muere.
- HUD del jugador reordenado: vida y maná apiladas arriba a la izquierda (antes maná estaba en
  el footer); carga se queda sola en el footer.
- **`AmbrosioLobo` con IA de combate funcionando** (2026-09-02): 7 animaciones (Guardia,
  Embestida, Zarpazo, Aullido, Transicion, GarraDeLuna, GarraDeLunaLanzamiento), máquina de
  estados por ciclo fijo verificada en motor real — Fase 1 (Vida > 50%): Guardia→Embestida→
  Zarpazo. Fase 2 (Vida ≤ 50%): Embestida→GarraDeLuna→Lanzamiento→Aullido. Embestida y Zarpazo
  pegan por contacto (con la misma ventana de invulnerabilidad de 0.8s que ya usaba Repintado);
  Lanzamiento dispara el proyectil `GarraLuna` hacia el jugador; Aullido crea una onda
  (`OndaAullido`) que crece con el tiempo y pega una vez por instancia. `Carta` y `FarolBomba` le
  hacen daño al jefe igual que a Repintado. Barra de vida grande y fija en el pie de pantalla
  (`BarraJefeFondo`/`BarraJefeFill`, 200 HP). Al llegar a 0 HP, congela el ciclo (`Fase=0`) y pasa
  a la pose `Transicion` — no hay pantalla de victoria todavía, solo se detiene.
  > [!warning] Placeholder de posición — no es la arena final
  > El jefe está parado en `Level1` (Barrio del Reloj) para poder testear la IA contra el
  > jugador ya armado, sin tener que duplicar toda su lógica de controles en una escena nueva.
  > Comparte pantalla con los 2 `Repintado` de nivel 1, lo cual no tiene sentido narrativo — la
  > idea es mudarlo a su propia escena (arena en la cima de la torre, fondo
  > `nivel3-corazon-toonaria.jpg`) cuando se arme el sistema de niveles/transición de escenas.
  > `OndaAullido` y la barra del jefe también son arte placeholder generado por mí (círculo y
  > rectángulo lisos), no dibujado — pendiente de reemplazar.

**No empezado**:
- Niveles 2 y 3 como escenas (el arte de fondo está listo, no importado).
- Escena dedicada de la arena del jefe (mudar `AmbrosioLobo` fuera de `Level1`, ver warning
  arriba) y pantalla de victoria/derrota del combate.
- Parry: el jugador todavía no puede parryear el proyectil `GarraLuna` — hoy solo pega daño
  directo. El doble salto y la esquiva/parry en sí (animaciones `SaltoDoble`/`Parry` ya
  importadas, ver Controles) siguen sin lógica de ningún tipo — el jugador no puede ejecutarlos
  todavía, son solo arte por ahora.
- Arte real de `OndaAullido` y de la barra de vida del jefe (hoy son placeholders geométricos).

**Cierre de pendientes que no dependían de arte nueva** (2026-09-02):
- **Doble salto**: implementado con `SetCanJump` (así se hace en GDevelop, el comportamiento no
  trae doble salto de fábrica) — un segundo salto en el aire, pose `SaltoDoble` sostenida 0.3s,
  se resetea al tocar el piso. Verificado sin errores.
- **Cooldown del parry**: 0.6s entre usos (antes se podía spamear sin costo).
- **Bloqueo de movimiento durante la muerte**: al entrar en `EstaMuerto`, se llama
  `IgnoreDefaultControls` sobre el comportamiento de plataformas — Ventura ya no puede
  deslizarse/saltar mientras está tirado en el suelo; se reactiva al reaparecer.
- **Pantalla de título**: escena nueva (`Titulo`, ahora la escena inicial del proyecto) con el
  logo (`logo-toonaria.jpg`, recortado a fondo transparente) y "Presioná ESPACIO para empezar",
  que lleva a `Level1`. Fondo oscuro acorde a la paleta del juego.

> [!bug] Segunda tanda de bugs reales, jugando de verdad (2026-09-02)
> Los arreglos anteriores no se vieron porque GDevelop de escritorio no relee el archivo solo
> mientras está abierto — quedó documentado para la próxima vez que pase. Con el proyecto
> recargado aparecieron bugs nuevos, reales, encontrados jugando:
> - **La carta salía gigante**: `carta-luna.jpg` nunca se había recortado a tamaño de ícono —
>   se usaba la imagen de referencia completa (1024x1024, prácticamente sin margen para
>   recortar, la ilustración ocupa todo el lienzo a propósito). El problema no era el recorte,
>   era que nunca se le puso un tamaño de render chico al crearla en pantalla. Ahora la carta,
>   el farol-bomba y la garra de luna del jefe se crean con un `ChangeWidth`/`ChangeHeight`
>   explícito (42x56, 48x48, 60x52 respectivamente) — como esto reescala también la máscara de
>   colisión automática, debería resolver de paso el "no hay hitbox" y "los enemigos no reciben
>   daño" (probablemente eran la carta gigante colisionando de forma rara, no una falla de
>   colisión en sí).
> - **Los sprites de Ventura tenían el texto de la etiqueta pegado en los pies** ("Idle", "Carga
>   1", etc.) y pedazos de las poses vecinas sangrando en los bordes — el recorte automático
>   original nunca los separó bien porque las 8 poses de la fila de arriba de `mov.jpg` están
>   literalmente tocándose en la ilustración original, sin espacio entre ellas. Se re-recortaron
>   las 11 poses con límites de columna manuales — mucho más limpio, aunque puede quedar algún
>   borde mínimo de una pose vecina en 2 o 3 casos (correr, salto-inicio, salto-aire).
>
> **Sin confirmar todavía — necesito que lo pruebes vos específicamente**: el doble salto. Leí
> el código fuente del comportamiento de plataformas del motor: por defecto permite volver a
> saltar sin soltar la tecla (`useRepeatedJump=true`), así que mi arreglo anterior debería
> alcanzar. Pero como ya reportaste que seguía roto una vez, necesito que me digas puntualmente
> qué pasa al apretar Espacio por segunda vez en el aire — ¿no pasa nada, o salta muy poco?

> [!bug] Tercera tanda — la animación de doble salto no existía de verdad (2026-09-02)
> Reportado: "no está la animación de doble salto o ese sprite cargado". Auditando el JSON del
> objeto `Player` de `Level1` directamente (no confiando ya en el validador, que da OK igual)
> encontré la causa real: una herramienta de edición del proyecto tiene un bug conocido — cuando
> se le pide agregar un elemento a un índice de array ya existente usando notación
> `animations[11]`, en vez de reemplazar el elemento crea una clave de texto literal
> `"animations[11]"` suelta al lado del array real. Las animaciones `SaltoDoble`, `Parry` y
> `Derrota` quedaron atrapadas así desde bastante antes en la sesión — pasaban la validación
> porque el JSON es válido, pero el motor nunca las leía porque no estaban dentro del array
> `animations` de verdad. Corregido reemplazando el array completo de una sola vez (14
> animaciones, en orden) y borradas las 3 claves sueltas. `ArenaJefe` no tenía este problema
> (se armó limpio desde el principio).

> [!bug] Cuarta tanda — sprites de Ventura "encimados" con las poses vecinas (2026-09-02)
> Reportado: "los sprites están muy encimados, deberías haber armado la plantilla de
> movimientos con más separación". Reabrí `mov.jpg` y medí a nivel de píxel (componentes
> conexos, no una grilla a ojo): confirmado que las 8 poses de la fila de arriba (Idle, Carga 1,
> Carga 2, Carga Completa, Correr, Salto-Inicio, Salto-Aire, Aterrizaje) están genuinamente
> pegadas sin ningún gap real entre la mayoría — el recorte manual anterior (tanda anterior de
> esta misma fecha) todavía dejaba pasar bordes de la pose vecina, visible como una figura
> parcial y una mano/sombrero flotante en los bordes de `ventura_correr.png`. Esto también
> explica por qué "al caminar Ventura no usa el sprite de caminar": la animación `Correr` sí se
> asignaba bien por evento (`SetAnimationName` en piso + moviéndose), pero el sprite en sí
> estaba contaminado y no se leía como una pose de carrera distinta.
> Recorté las 11 poses de nuevo con etiquetado de componentes conexos (cada pose es su propia
> mancha de píxeles aislada de las vecinas, no una caja rectangular) en vez de coordenadas
> manuales. Un caso (Carga 2 / Carga Completa) sí estaba fusionado a nivel de píxel — capa y
> farol de uno tocan el otro — resuelto con un corte por fila que sigue el hueco real entre las
> dos figuras en vez de una sola línea vertical fija, más una limpieza final descartando
> cualquier isla de píxeles desconectada del personaje principal. Confirmado sin fragmentos
> sueltos en las 11 poses. Reemplazados los 11 PNG en `assets/ventura/`.

> [!bug] Bugs reales encontrados jugando con las manos (2026-09-02)
> Hasta acá todo lo había verificado con el motor corriendo solo, sin tocar teclas — nunca había
> probado los controles de verdad. Al jugarlo aparecieron varios problemas reales, todos
> corregidos en `Level1` y `ArenaJefe`:
> - **El salto no alcanzaba a esquivar enemigos**: con la física original (jumpSpeed 600,
>   gravedad 1500) la altura máxima de salto daba ~120px, y los enemigos miden 237px de alto —
>   era matemáticamente imposible saltarlos. Subido `jumpSpeed` a 900.
> - **Las cartas no se cargaban en el aire**: el evento de carga exigía estar parado en el piso.
>   Si saltabas para esquivar y cargabas en el aire (lo más natural en combate), nunca arrancaba
>   la carga → nunca salía ninguna carta → los enemigos nunca recibían daño. Se sacó esa
>   restricción.
> - **El doble salto se gastaba solo**: el disparador no distinguía entre "mantener apretada la
>   tecla del primer salto" y "apretarla de nuevo en el aire" — se consumía automáticamente
>   apenas se dejaba el piso, así que nunca quedaba disponible cuando se lo quería usar de
>   verdad. Se agregó un rastreo de pulsación nueva (`SaltoKeyEstabaPresionado`).
> - **Se sentía "congelado" al recibir daño**: no había ningún empuje al golpear, así que si
>   Ventura quedaba pegado a un enemigo, seguía recibiendo daño cada 0.8s sin despegarse. Se
>   agregó un empuje horizontal hacia atrás al recibir un golpe.
>
> **No corregido porque no es un bug**: la animación `Correr` es una sola pose estática (no un
> ciclo de caminata animado, por las limitaciones de arte ya conocidas) — cambia de verdad al
> moverse, pero al ser un solo frame puede no notarse como "caminar". Si se ve mal en la próxima
> prueba, hay que pedir un segundo frame de esa pose.
>
> **Importante**: estas correcciones se basan en leer la lógica con cuidado, no en probarlas con
> teclado de verdad — mis herramientas no pueden simular eso. Hace falta que se prueben jugando
> para confirmar que están resueltas.

> [!success] Arena del jefe terminada (2026-09-02)
> Escena `ArenaJefe` armada de cero: pantalla fija sin scroll (no necesita cámara), con el
> jugador completo (mismas mecánicas que Level1, con nombre `PlayerA` para no chocar con el
> `Player` de Level1) y `AmbrosioLobo` con su ciclo de 2 fases funcionando — verificado en motor
> real, se lo vio moverse (Embestida acercándose a Ventura) y atacar. Carta/FarolBomba le hacen
> daño, el parry devuelve `GarraLuna`, la barra grande del jefe se actualiza. Pendiente:
> pantalla de victoria/derrota (el jefe a 0 HP hoy solo congela el ciclo, no pasa nada más).
>
> **Segundo bug real encontrado en el camino**: al copiar el comportamiento de plataformas del
> jugador a la escena nueva, alcanza con poner `{name, type}` sin las propiedades numéricas
> (gravedad, velocidad de salto, etc.) para que el editor lo acepte como válido — pero en este
> motor/exportador, sin esas propiedades explícitas el personaje deja de dibujarse en tiempo
> real (posición inválida), aunque sus variables se sigan leyendo bien. Conclusión: cualquier
> objeto con `PlatformerObjectBehavior` en una escena nueva necesita las propiedades completas
> copiadas de una que ya funcione, no alcanza con el tipo solo.
>
> **Tercer hallazgo, más una limitación de la herramienta que un bug**: renombrar un objeto
> (`Player` → `PlayerA`) actualiza los parámetros simples de los eventos, pero NO el texto
> dentro de fórmulas (`Player.Variable(Vida)` dentro de una expresión más larga se queda con el
> nombre viejo) — hubo que corregir esas fórmulas a mano.

> [!bug] Bug real encontrado y resuelto (2026-09-02) — FixCamera/ClampCamera rompen el render
> Al armar la cámara con scroll, usar `FixCamera` (o `CenterCameraOnObject` + `ClampCamera`) hace
> que Ventura y todo el HUD dejen de renderizarse en este motor/exportador — sin ningún error
> visible en consola. Lo aislé probando versiones sucesivas del proyecto hasta encontrar el
> evento exacto responsable. La solución: un objeto invisible (`CameraAnchor`, 1x1px) cuya
> posición se calcula a mano con `min(max(Player.X(),640),4480)` cada frame, centrando la cámara
> en ese objeto con `CenterCameraOnObject` (que sí funciona bien solo) en vez de dejar que el
> límite lo ponga la propia instrucción de cámara. Anotado acá porque si en algún momento hace
> falta otra cámara con límites (nivel 2, nivel 3, la arena del jefe), hay que usar este mismo
> truco del ancla, no `FixCamera`/`ClampCamera` directo.

**Lo que sigue sin resolverse porque sí depende de arte o de una decisión de diseño mayor**:
- Escena real de la arena del jefe (el jefe sigue de prueba en `Level1`, ver warning más arriba)
  — no es un problema de arte sino de arquitectura (compartir la lógica del jugador entre
  escenas sin duplicarla), evaluar aparte.
- Pantalla de Game Over / límite de vidas — hoy el respawn es infinito e inmediato a propósito,
  no se decidió todavía si el juego debería tener un límite.
- Niveles 2 y 3, prólogo, sonido, farol-bomba real — todos bloqueados por arte o assets que
  todavía no existen.

**Muerte y respawn de Ventura** (2026-09-02, agregado a pedido): al llegar a 0 de vida, Ventura
queda congelado 2 segundos con la pose `Derrota` (`EstaMuerto`/`TiempoMuerte`) y reaparece en el
punto de partida del nivel (100, 400) con la vida llena y un instante de invulnerabilidad
(reutiliza `TiempoInvulnerable`, no hace falta variable nueva). No bloquea el movimiento del
jugador durante esos 2 segundos (podría deslizarse/saltar mientras está "muerto") — pendiente de
ajustar cuando se vea cómo se siente en juego. No hay pantalla de "Game Over" ni límite de
vidas: por ahora el respawn es inmediato e infinito.
- Prólogo/tutorial como escena de flashback (hoy no existe, `Level1` funciona directo como
  primer nivel real).
- Pantalla de título, menú, game over, transición entre escenas.
- Sonido (música, efectos) — ni empezado.
- Export/build real probado con `gdexporter` — instalado, nunca corrido contra este proyecto.

> [!bug] Auditoría del proyecto contra la doc oficial de GDevelop (2026-09-02)
> Con la skill `gdevelop-official-docs` recién instalada, audité `game.json` completo (no una
> lectura superficial: recorrí el JSON entero buscando patrones de bug ya conocidos en esta
> sesión, y crucé nombres de propiedades de comportamientos contra la wiki oficial). Encontrado
> y resuelto:
> - **Restos de claves JSON sueltas** (mismo bug de la herramienta de edición documentado antes,
>   `set_object_property` con índice de array existente) en `AmbrosioLobo` (`GarraDeLuna`,
>   `GarraDeLunaLanzamiento`, ver punto siguiente — quedó irrelevante porque se borró el objeto
>   entero) y en `Logo` de `Titulo` (una entrada `animations[0]` duplicada exacta de la animación
>   `Default` que ya estaba bien en el array real — borrada, sin efecto en el juego).
> - **Un jefe fantasma completo dentro de `Level1`**: 43 eventos (36% del event sheet de ese
>   nivel) más 5 objetos (`AmbrosioLobo`, `GarraLuna`, `OndaAullido`, `BarraJefeFondo`,
>   `BarraJefeFill`) con **cero instancias puestas en la escena** — el comentario del propio
>   evento lo explicaba: era un placeholder para probar la IA del jefe antes de que existiera
>   `ArenaJefe`, con la nota "se va a mudar cuando se cree esa escena" nunca ejecutada. `ArenaJefe`
>   ya tiene su propia copia funcionando y probada, así que este bloque en `Level1` nunca corría
>   (nada lo disparaba) — puro peso muerto, difícil de explicar en una defensa oral si alguien
>   pregunta por qué el nivel 1 tiene lógica de un jefe que no está ahí. Confirmado con
>   `preview_scene` antes y después: mismo render exacto, cero impacto jugable. `Level1` quedó en
>   76 eventos y 19 objetos (antes 119 y 24).
> - **Revisado y descartado como problema real**: el warning
>   `[PIXI Image manager] Unable to find texture for resource ""` que aparece en cada
>   `preview_scene` — no corresponde a ningún recurso, sprite ni efecto de capa del proyecto
>   (barrido completo del JSON sin resultado), así que es un pedido interno del motor por una
>   textura placeholder/vacía, no un recurso roto nuestro. El uso de `FixCamera`/`ClampCamera`
>   que aparecía en la búsqueda de texto completo eran sólo menciones dentro de comentarios de
>   evento (explicando por qué NO se usan), no llamadas reales — el workaround de `CameraAnchor`
>   sigue siendo el único camino de cámara en el proyecto.
