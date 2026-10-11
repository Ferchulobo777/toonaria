# Game Design Document — Toonaria

Trabajo integrador de **Multimedia y Juegos en Web** — Tecnicatura Universitaria en Desarrollo
Web, FCAD, UNER, 2026. Equipo: Fernando Rubén Bareiro Ruiz, Mateo Fernández, Natalia Ailén
González y Fernando Rodríguez.

Sigue la plantilla de GDD de la cátedra (Unidad 3), en su mismo orden. Las secciones que no
aplican a este juego quedan con el motivo. El guion escena por escena está en
[`Guion.md`](Guion.md) y la ficha de personaje en
[`Ficha-Personaje-Ventura.md`](Ficha-Personaje-Ventura.md).

Versión 1.0 — 2026-10-11 (entrega final). La bitácora de decisiones y problemas resueltos va al
final, separada del diseño.

---

## Objetivos del juego

**Gran concepto**: *Bloodborne, pero dibujo animado*. Una ciudad victoriana de tinta y niebla,
dibujada como un cartoon de los años 30 (estilo *rubber-hose*), donde la luna llena "repinta" a
la gente y la convierte en monstruos. El tono gótico lo dan la ambientación y la historia; el
estilo animado lo vuelve accesible y propio.

**Reverso de la caja**:
- El arma es un **mazo de cartas que se carga**: soltar rápido tira una carta débil y barata;
  aguantar tira una fuerte que cuesta más maná y frena al personaje. Cada disparo es una decisión.
- El **parry devuelve** lo que te tiran (máscaras, garras de luna). El jefe final está pensado para
  que el parry sea la herramienta más rentable de la pelea.
- **Historia y mecánica se enseñan juntas**: el tutorial es el recuerdo en el que Ambrosio, el
  mentor, enseña a pelear; el jefe final es Ambrosio transformado.

**Funciones de red**: no tiene (un jugador, sin conexión).

## Descripción general de la historia

En Toonaria, cada luna llena "sobre-tiñe" a quienes la miran de más: el **Repintado**. Ambrosio,
el farolero que encendía los faroles del barrio, fue el primero: se convirtió en un lobo y
desapareció hacia el centro de la ciudad. **Ventura**, el cartomante al que Ambrosio le enseñó el
oficio, cruza la ciudad barrio por barrio para encontrarlo, volviendo a encender sus faroles en el
camino.

Las ubicaciones se conectan como un viaje hacia el centro: la carpa de Ambrosio (el recuerdo),
el Barrio del Reloj, el Barrio de los Teatros, el Corazón de Toonaria y la cima de la torre del
reloj. Cada barrio está más corrompido que el anterior.

**Final**: Ventura derrota al lobo y Ambrosio vuelve a ser él mismo, débil. Ahí se revela por qué
Ventura nunca se transformó: nunca miró la luna de frente, la lee reflejada en la laca de sus
cartas. Es el oficio que Ambrosio le enseñó, no un don. El final queda abierto: la próxima luna
va a volver.

Estructura en tres actos (monomito, Unidad 2): prólogo y nivel 1 (el llamado), niveles 1 y 2 (el
camino de las pruebas), nivel 3 y jefe (la reconciliación con el mentor, que es literalmente el
enemigo final).

## Controles del juego

| Acción | Teclado |
|---|---|
| Moverse | Flechas ← → o A / D |
| Saltar / doble salto | Espacio, W o ↑ (mantener = más alto) |
| Carta lunar | Mantener X o J para cargar, soltar para tirar |
| Farol incendiario | C o K |
| Parry | Z o L, justo antes del golpe |
| Pasar diálogo | Enter (también Espacio, X o Z) |
| Pausa | Esc (Q en pausa vuelve al título) |

Cada acción tiene dos teclas: una para la mano izquierda (WASD + J/K/L) y otra para jugar con las
flechas (X/C/Z). Plataforma única: teclado en navegador.

## Requerimientos tecnológicos

- **Motor**: GDevelop 5 (5.6), exportación HTML5. Resolución 640 × 360 escalada sin suavizado.
- **Creación de niveles**: los mapas se escriben como grillas de texto (una letra por celda de
  16 px) y un script los convierte en instancias. Ver "Implementación" en el Apéndice.
- **Generación del proyecto**: `herramientas/construir_juego.py` arma `juego/game.json` completo
  (objetos, eventos, escenas). El proyecto se abre y se juega normalmente en el editor.
- **Debug**: validadores de eventos y expresiones contra el propio motor, y un probador que juega
  con teclas reales en un navegador sin ventana (`herramientas/probar_juego.mjs`). En el juego,
  el menú "Capítulos" permite saltar a cualquier nivel o al jefe.

## Parte frontal del juego

Al arrancar: pantalla de carga de GDevelop (con su logo, requisito de la versión gratuita del
motor) y directo al título. Los créditos del equipo y de la cátedra están en el menú del título y
al final del juego. Licencia del repositorio: GPLv3.

## Cutscene description

No hay cinemáticas de video: las escenas narrativas son **diálogos en el motor**, con la caja de
texto y los retratos, mientras los personajes siguen visibles en el escenario. El jugador las
avanza con Enter.

| Momento | Escena |
|---|---|
| Inicio del prólogo | Ambrosio corrige a Ventura: "Cortá, cargá, soltá. En ese orden." |
| Fin del prólogo | La regla de la luna: "A la luna llena la mirás una vez." |
| Inicio del nivel 1 | Años después. Ventura se lleva el farol de Ambrosio sin encenderlo. |
| Fin del nivel 1 | El farol apagado del puesto de Ambrosio, con una carta morada clavada |
| Fin del nivel 2 | Un actor repintado repite "cortá, cargá, soltá" sin saber a quién cita |
| Fin del nivel 3 | Huellas de garras; Ventura enciende el farol |
| Encuentro con el jefe | "Ambrosio." El lobo gruñe. "Cortá, cargá, soltá." |
| Cambio de fase | Ambrosio aparece dentro del lobo: "Ven... tura..." |
| Derrota del jefe | La conversación final y la revelación de la laca |
| Epílogo | Cuatro frases sobre negro y los créditos que suben |

## Attract mode description

No tiene. Es una herencia del arcade para atraer público en el local; en un juego web que el
jugador ya eligió abrir no aporta. El título igual está vivo: nubes y bruma que se mueven, el logo
que flota y la música.

## Título / pantalla de inicio

Fondo pixelizado de nuestra ilustración del Corazón de Toonaria, con la torre y la luna detrás
del logo. Animaciones: nubes y bruma desplazándose, logo flotando, Ventura en la esquina. Música:
vals en Re menor con caja de música.

Opciones (arriba/abajo y Enter): **Jugar**, **Capítulos**, **Controles**, **Créditos**. No hay
guardado de partida: los capítulos cumplen esa función. No hay opciones de video o audio: la
resolución es fija y el volumen se maneja desde el navegador.

## Otras pantallas

- **Capítulos**: lista de las cinco escenas jugables (prólogo, tres niveles y la torre), todas
  disponibles desde el inicio. Lo decidimos así porque es una entrega para mostrar y defender:
  poder ir directo al jefe importa más que obligar a desbloquearlo.
- **Controles** y **Créditos**: paneles sobre el título, sin cambiar de escena.
- **Pausa**: dentro de cada nivel.
- **Final**: epílogo y créditos que suben sobre la torre; vuelve al título.

No hay contenido desbloqueable, galería ni trucos.

## Diagrama de flujo

```
Título ─┬─ Jugar ──────► Prólogo ► Nivel 1 ► Nivel 2 ► Nivel 3 ► Arena del jefe ► Final ─┐
        ├─ Capítulos ──► cualquiera de las cinco escenas jugables                         │
        ├─ Controles                                                                      │
        └─ Créditos                                                                       │
   ▲                                                                                      │
   └──────────────────── (Pausa → Q, o al terminar los créditos) ◄──────────────────────┘
```

No hay *game over*: al morir, Ventura reaparece en el último farol encendido.

## Pantalla de carga

La de GDevelop (barra de progreso sobre fondo oscuro). El juego completo pesa poco (pixel art y
audio comprimido), así que carga en segundos y no justifica tips ni minijuegos de espera.

## Cámara del juego

Desplazamiento lateral 2D con seguimiento suave:
- Persigue un punto **36 px adelante** de hacia donde mira Ventura, para mostrar más de lo que
  viene, con suavizado exponencial (no se pega al personaje).
- Los límites del nivel se aplican a mano en vez de con la acción de cámara del motor, para poder
  sumar el **temblor** (golpes, explosiones, jefe) después del límite.
- **Parallax**: cielo, nubes lejanas, ciudad, nubes cercanas y bruma por delante de la acción. El
  factor de la ciudad se calcula para que la tira ilustrada de cada barrio cubra exacto el nivel.
- En la carpa y en la arena (interiores) no hay cielo ni nubes; la arena es una pantalla fija.

## Sistema HUD

- Arriba a la izquierda: retrato de Ventura, **5 cartas de vida** (20 cada una; media carta = 10)
  y **barra de maná**.
- **Medidor de carga** flotante sobre la cabeza, sólo mientras se carga: la información aparece
  donde el jugador está mirando.
- **Avisos** centrados arriba (farol encendido, casco que frena cartas).
- **Barra del jefe** abajo al centro, con su nombre: cambia de "Ambrosio, el Farolero" a
  "Ambrosio, el Lobo" en la fase 2.
- **Caja de diálogo** con el retrato de quien habla (Ventura, Ambrosio, el Actor, el lobo),
  efecto de máquina de escribir e indicador para seguir.

Lo que no está en el HUD se transmite en el personaje: parpadeo de invulnerabilidad, destello
violeta en los enemigos golpeados, cámara lenta de golpe.

## Personaje del jugador

**Ventura** (Buenaventura): cartomante de un barrio viejo de Toonaria. Sombrero de ala ancha con
dije de luna, levita, mazo de cartas moradas. **Motivación**: encontrar a Ambrosio, su mentor, que
le enseñó a leer la suerte y a pelear. Es el único que puede cruzar la ciudad bajo la luna sin
transformarse.

## Medidas del jugador

Pixel art de 48 px de alto. Comportamiento de plataformas de GDevelop, ajustado a mano:

| Medida | Valor | Por qué |
|---|---|---|
| Velocidad máxima | 150 px/s (90 cargando) | Cargar una carta fuerte cuesta movilidad |
| Gravedad subiendo / cayendo | 1200 / 1600 | Gravedad asimétrica: el personaje no "flota" al bajar |
| Velocidad de salto | 427, sostén 0,3 s | Salto corto ~38 px tocando, completo ~75 px manteniendo |
| Doble salto | Un salto más en el aire; anula la caída | Rinde igual aunque se use bajando |
| Coyote time | 0,1 s | Se puede saltar un instante después de pisar el vacío |
| Buffer de salto | 0,12 s | Apretar un poco antes de tocar el piso igual salta |
| Caja de colisión | 16 × 40 px | Los faldones y el ala del sombrero no "tocan" peligros |
| Al recibir daño | 1 s invulnerable, 0,22 s sin control, empuje 170 px/s | Ver "Vida" |

No se agacha ni se cuelga de bordes: ningún peligro ni ataque del juego lo requiere. Las 18
animaciones están en `juego/assets/pixel/ventura/`.

## Habilidades del jugador

**Carta lunar (arma principal)**: la carga sube 150 por segundo (llena en 0,67 s) y define el
nivel de la carta.

| Carga | Carta | Daño | Maná | Velocidad |
|---|---|---|---|---|
| 0 – 44 | Débil | 8 – 22 | 4 – 11 | 300 – 366 px/s |
| 45 – 89 | Media | 22 – 36 | 11 – 18 | 368 – 434 px/s |
| 90 – 100 | Completa | 37 – 40 | 18 – 20 | 435 – 450 px/s |

**Farol incendiario (arma secundaria)**: el farol de Ambrosio como granada. Sale en arco con
gravedad propia, explota al tocar piso o enemigo y daña en área **una sola vez** (35). Cuesta 30
de maná y tiene 0,8 s de enfriamiento.

**Parry**: ventana de 0,2 s y enfriamiento de 0,45 s. Es una apuesta de *timing*, no un escudo.

| Contra | Resultado |
|---|---|
| Embestida del Repintado | Queda aturdido 1,2 s, +15 maná |
| Máscara del Actor, garra de luna del jefe | Vuelve 1,8 veces más rápida, +15 maná; hace 30 a enemigos y 40 al jefe |
| Zarpazo del jefe | Queda aturdido 1 s, +20 maná |

No hay progresión de habilidades: todo el kit se enseña en el prólogo y se pone a prueba en los
niveles. Mejorar el mazo entre niveles queda como expansión.

## Herramientas de inventario

No hay inventario ni equipamiento: las dos armas y el parry están siempre disponibles y el único
recurso es el maná. Combate:
- **Reacciones**: cada golpe produce destello violeta, chispa, cámara lenta de 2 a 10 cuadros y
  temblor de cámara según su peso.
- **Combos**: no hay cadenas de botones; la combinación está en la táctica (parry que devuelve la
  garra mientras se carga la siguiente carta, castigar al jefe atascado con una carta completa).

## Potenciadores / modificadores de estado

| Objeto | Efecto | Duración |
|---|---|---|
| Té | +30 de vida | Instantáneo |
| Fragmento de luna | +40 de maná | Instantáneo |
| Farol encendido (checkpoint) | Vida completa y nuevo punto de reaparición | Hasta el próximo farol |
| Invulnerabilidad | Tras un golpe (1 s) o al reaparecer (1,2 – 1,5 s) | Temporal, con parpadeo |

Ninguno modifica los controles.

## Vida

- 100 de vida, en 5 cartas del HUD. Se repone con té y al encender un farol.
- **Peligros del escenario** (charcos, rejas, engranajes, péndulos): 12 de daño.
- **Pozos**: −25 de vida y vuelta al último farol, con fundido rápido.
- **Muerte**: pose de derrota, fundido y reaparición en el último farol con vida y maná completos.
  El castigo es perder el tramo recorrido, no los recursos. No hay vidas limitadas ni *game over*.
- Contra el jefe, morir reinicia la pelea entera (ver Jefes).

## Score

No tiene puntaje: el objetivo es llegar y la historia es la recompensa. Un puntaje empujaría a
jugar distinto (farmear enemigos) de lo que pide el diseño (avanzar y aprender patrones).

## Recompensa y economía

No hay moneda ni tienda. Las recompensas son té y luna (escondidos en rutas altas o que sueltan
los enemigos y barriles al azar) y los avances de la historia al final de cada nivel.

## Vehículos

No aplica.

## Personajes principales de la historia

| Personaje | Relación con el jugador | Dónde aparece |
|---|---|---|
| **Ventura** | El protagonista | Todo el juego |
| **Ambrosio, el Farolero** | Mentor; le enseñó el oficio y le dejó el farol | Prólogo (humano), jefe final (lobo), final |
| **El Actor del eco** | Un repintado que repite las palabras de Ambrosio | Final del nivel 2 |
| **Los Repintados** | Vecinos transformados: enemigos que asustan pero dan pena | Niveles 1 a 3 |

## Esquema de progresión del juego

| Escena | Duración aprox. | Historia | Qué se aprende o se pone a prueba |
|---|---|---|---|
| Prólogo | 3 – 5 min | El recuerdo; la regla de la luna | Mover, saltar, doble salto, cartas, carga, farol, parry |
| Nivel 1 | 6 – 8 min | El llamado; la carta morada | Repintado, pozos, toldo, engranajes, andamio, tablones |
| Nivel 2 | 7 – 9 min | El eco de Ambrosio | Actor (parry a proyectiles), Cuervo, péndulos, tramoya |
| Nivel 3 | 8 – 10 min | Ventura enciende el farol | Agente (carga obligatoria), nubes, escalinata, todo junto |
| Jefe | 4 – 8 min | La reconciliación | Leer patrones, castigar, devolver garras |

No se ganan habilidades nuevas: todas se aprenden en el prólogo y cada nivel exige más de ellas.

## Clasificación de la jugabilidad

Plataformas (saltos de precisión, plataformas móviles y que se rompen) y combate a distancia
(carga, gestión de maná, parry). Sin sigilo, conducción ni vuelo.

## Pantalla de selección de nivel / navegación

El menú "Capítulos" del título lista las cinco escenas con sus nombres; se navega con
arriba/abajo y Enter. Dentro del juego el avance es lineal: cada nivel termina en la escena
siguiente.

## Mecánicas universales

| Elemento | Comportamiento |
|---|---|
| Suelo y cornisas | Las cornisas se atraviesan desde abajo |
| Toldo elástico | Rebote alto (~120 px) sólo si se cae desde arriba; devuelve el doble salto |
| Tablón podrido | Cruje 0,45 s (tiembla), cae, vuelve a los 3 s: el camino nunca queda cerrado |
| Andamio móvil | Va y viene con movimiento senoidal: se frena en los extremos para que se pueda medir |
| Nube de tinta | Sube y baja; se atraviesa desde abajo |
| Caedor de engranajes | Suelta un engranaje con ritmo fijo; hay que leer el patrón |
| Péndulo | Oscila ±55°; los vecinos están desfasados |
| Barril | Plataforma que se rompe con cartas o farol y puede soltar té o luna |
| Farol de gas | Checkpoint: se enciende al tocarlo |
| Reja de salida | Termina el nivel |
| Zonas de diálogo | Invisibles; disparan una conversación una sola vez |
| Bordes del nivel | Paredes invisibles: no se puede salir del mapa por el costado |

## Niveles del juego

Cada nivel sigue el ciclo **presentar → practicar → combinar**: una idea nueva aparece sola y
sin riesgo, después con presión y al final mezclada con lo anterior. Los fondos salen de nuestras
ilustraciones de cada barrio, encadenadas en una tira continua con parallax.

**Prólogo — La carpa de Ambrosio**. 1152 px, interior de día en sepia, música de acordeón.
*Objetivo*: aprender el kit completo. Circuito de entrenamiento donde cada estación enseña una
acción y Ambrosio la presenta con su voz: un cajón bajo y uno alto (salto corto y completo), una
pila de 80 px (doble salto: un píxel más que el salto completo), barriles (cartas y farol) y la
lección de parry. Ambrosio tira cartas lentas de práctica y una barrera invisible no deja seguir
hasta devolver una: es la mecánica que decide la pelea final. *Recompensa*: la regla de la luna.

**Nivel 1 — Barrio del Reloj**. 3840 px, música "barrios". *Objetivo*: llegar al puesto de
Ambrosio. 8 Repintados, charcos, un toldo hacia una ruta alta con premio, caedores de engranajes,
rejas, un pozo de 288 px con andamio móvil, tablones podridos con ruta alternativa por nubes de
tinta, 3 faroles. *Recompensa*: la carta morada clavada en el farol apagado.

**Nivel 2 — Barrio de los Teatros**. 4096 px, música "barrios". *Objetivo*: cruzar la calle de
los teatros. Presenta al Actor y al Cuervo y la tramoya: 4 Actores, 5 Cuervos, 2 Repintados,
4 péndulos (bolsas de arena), 8 tablones sobre el foso del escenario, dos andamios en un foso de
416 px y 2 toldos, 3 faroles. *Recompensa*: el eco de Ambrosio.

**Nivel 3 — El Corazón de Toonaria**. 4352 px, música "corazón". *Objetivo*: llegar a la puerta
de la torre. Presenta al Agente y exige todo: 4 Agentes, 2 Actores, 3 Cuervos, 2 Repintados,
3 péndulos de reloj, caedores, un foso de 512 px que sólo se cruza por 4 nubes de tinta, la
escalinata (recorrido vertical con un descanso custodiado) y rejas, 3 faroles. *Recompensa*:
Ventura enciende el farol.

**Arena — La cima de la torre**. Una pantalla, detrás del reloj gigante con la luna. Piso de
hierro y dos cornisas altas (se llega con doble salto) que sirven de refugio contra la embestida;
desde arriba las cartas pasan por encima del jefe, así que para pegarle hay que volver a bajar.

## Reglas generales de los enemigos

- **Comportamientos**: patrulleros que cuidan su tramo (rango calculado desde su posición
  inicial; ninguno cruza el nivel), tirador a distancia y volador que se lanza en picada.
- **Detección**: por distancia horizontal y diferencia de altura con Ventura.
- **Aviso obligatorio**: todos telegrafían su ataque con una pose y un sonido propios (gruñido,
  "¡ta-dá!", graznido, silbato), así se los reconoce sin mirar.
- **Golpes**: destello violeta y animación de golpe sin cortar su aviso o su ataque.
- **Derrota**: animación de derretirse en tinta; puede soltar té (1/3) o luna (1/3).
- **Implementación**: los cuatro forman el grupo `Enemigo` y comparten la lógica de recibir
  cartas y explosiones, el contacto y la muerte; cada uno tiene su propia máquina de estados.

## Enemigos específicos por nivel

| Enemigo | Nivel | Vida | Daño | Patrón | Cómo se vence |
|---|---|---|---|---|---|
| **Repintado** (Mr. Pennypencher) | 1 – 3 | 30 | 8 contacto, 15 embestida | Patrulla. Cerca: levanta las garras 0,5 s, embiste 0,35 s, se recupera 0,8 s | Saltar la embestida o hacerle parry; castigar en la recuperación |
| **Actor** | 2 – 3 | 24 | 12 la máscara | Se planta a 210 px, "¡ta-dá!" y tira una máscara recta al pecho | Saltarla o devolverla; acercarse en la pausa de 1,4 s |
| **Cuervo** | 2 – 3 | 10 | 10, 14 en picada | Vuela en su zona; si Ventura pasa abajo se frena 0,4 s y se tira en picada hacia donde estaba | Moverse durante el aviso: la dirección se fija al empezar |
| **Agente** | 3 | 70 | 12 contacto, 14 la onda | Lento; silbato y garrote en alto 0,75 s, golpea el piso y suelta dos ondas | Saltar las ondas. El casco frena las cartas débiles: cargar o usar el farol |

La primera vez que una carta débil rebota en el casco aparece en pantalla "El casco frena las
cartas débiles: cargá antes de tirar": la regla se enseña en el momento en que importa.

## Jefes

**Ambrosio, el lobo de la luna**. 92 px de alto (el doble que Ventura), 320 de vida. Pelea **por
patrones, no reactiva**: cada fase repite un ciclo fijo que se puede aprender, como en Cuphead o
Bloodborne. Lo único que cambia con la vida que le queda es el **ritmo**: en la fase 2 los avisos
se acortan hasta un 60 %, sin cambiar el orden.

**Escena de intro**: diálogo del encuentro, en silencio; la música empieza con el primer aullido.

**Fase 1 — "El Farolero"** (320 → 160). Ciclo: Embestida → Zarpazo.

| Ataque | Aviso | Golpe | Respuesta |
|---|---|---|---|
| Embestida | Se agacha y gruñe (1 s) | Corre recto a 300 px/s hasta la pared (25) | Doble salto por encima o subir a una cornisa. **Queda atascado 1,5 s: punto débil, las cartas hacen 50 % más** |
| Zarpazo | Se acerca acechando y levanta la garra (0,55 s) | Arco corto delante (20) | Alejarse, o parry: queda aturdido 1 s |

**Transición** (al 50 %): Ambrosio aparece un instante dentro del lobo y habla. Se limpian los
ataques en el aire para que el diálogo no sea una trampa.

**Fase 2 — "El Lobo"** (160 → 0). Ciclo: Embestida → Garra de luna → Aullido.

| Ataque | Aviso | Golpe | Respuesta |
|---|---|---|---|
| Embestida | Más corto | 370 px/s, atascado 1,1 s | Igual que en la fase 1, con menos margen |
| Garra de luna | Junta las garras al pecho, brillo morado | 3 medialunas al pecho, una cada 0,32 s (18 c/u) | Saltarlas, o devolverlas: 40 al jefe cada una |
| Aullido | Se para en dos patas | Dos ondas de luna por el piso hacia los dos lados (16) | Saltarlas: llegan a las paredes, alejarse no alcanza |

**Cómo se derrota**: castigando cada embestida mientras está atascado y devolviendo garras. Si
Ventura muere, la pelea se reinicia entera (vida, fase y posición): si el jefe conservara el
daño, perder no costaría nada. **Recompensa**: Ambrosio vuelve a ser él, la conversación final y
el epílogo.

## NPCs

**Ambrosio en el prólogo**: NPC de instrucción. Presenta cada estación del circuito, mira siempre
a Ventura, la espera en la última estación y le tira cartas de práctica para el parry. Diálogos
completos en `Guion.md` y en `herramientas/construir_juego.py` (`DIALOGOS_PROLOGO`).

**El Actor del eco** (nivel 2): NPC ambiental, no ataca; dispara el diálogo de cierre del nivel.

## Objetos coleccionables

No hay coleccionables que se cuenten. Los fragmentos de luna y el té escondidos en rutas altas
(cornisas a las que se llega con toldo o doble salto) premian explorar con recursos, no con
contenido desbloqueable.

## Minijuegos

No tiene.

## Escenas secundarias

No hay misiones secundarias. Las rutas altas opcionales de cada nivel (toldo → cornisa con
premio, nubes de tinta sobre los tablones) son el contenido alternativo.

## Música y efectos de sonido

Todo el audio se genera por código (`diseno/audio/`) con las herramientas de las consolas de 8 y
16 bits: ondas cuadradas, triangulares, diente de sierra y ruido, con envolventes. Es coherente con
el pixel art y cada sonido queda escrito como una receta que se puede ajustar.

| Tema | Dónde | Sentimiento buscado |
|---|---|---|
| Título y final | Menú, epílogo | Vals en Re menor con caja de música: nostalgia (la caja es de la carpa) |
| Carpa | Prólogo | Fa mayor en 6/8 con acordeón, el único en modo mayor: el pasado feliz |
| Barrios | Niveles 1 y 2 | La menor con sol sostenido, bajo saltarín: cartoon de terror travieso |
| Corazón | Nivel 3 | Mi menor con acorde napolitano y campana de reloj: tensión |
| Jefe | Arena | Mi menor a 160 pulsos, bajo constante: algo que se descompone |

Los temas hacen bucle sin corte. **41 efectos**: cada acción del jugador tiene respuesta
inmediata; cada enemigo, un aviso reconocible; lo que recompensa sube de altura (té, luna, farol,
parry) y lo que castiga baja (daño, caída, derrota).

## Puntos y preocupaciones / Apéndice

**Preocupaciones abiertas** (para ajustar con jugadores reales):
- Dureza del jefe (320 de vida, ritmo de la fase 2).
- La tramoya del nivel 2 (andamios con cuervos encima) puede ser el tramo más frustrante.
- Tiempos reales de cada nivel.

**Expansiones posibles** (fuera del alcance): una versión mini-jefe de Mr. Pennypencher (el
Repintado del delantal) con ataques propios; controles táctiles; mejoras del mazo entre niveles;
publicación en itch.io.

**Texto del juego**: los diálogos completos están en `Guion.md` y en los diccionarios
`DIALOGOS_*` de `herramientas/construir_juego.py`.

### Arte

- **Pixel art de 48 px** en lienzo de 96 × 64 y paleta cerrada de 20 colores "tinta + morado"
  (`diseno/arte/pipeline/paleta.py`).
- **Personajes**: las hojas de animación parten de nuestro arte de personajes
  (`diseno/arte/personajes/`) y pasan por nuestro proceso de pixelizado (`pixelizar.py`): recorte del fondo, escala común por personaje, cuantización a la paleta en
  espacio Lab, prioridad al contorno de tinta, ajuste de la grilla y anclaje común para que no
  "tiemblen". `ventura.py` y `enemigos.py` arman cada animación; los idle se hacen a mano
  desplazando el torso, así el personaje quieto no "hierve".
- **Fondos**: nuestras ilustraciones de cada barrio (`diseno/arte/escenarios/`) se encadenan con
  un fundido de niebla, se pixelizan con trama ordenada y se separan en capas
  (`fondos_ilustrados.py`).
- **Geometría pura** (tiles, proyectiles, efectos, HUD, obstáculos): dibujada por código
  (`objetos_juego.py`, `obstaculos.py`) porque necesita exactitud de grilla.
- Las ilustraciones quedan en `diseno/arte/` y los scripts en `diseno/arte/pipeline/`: los
  assets del juego se pueden regenerar desde ahí.

### Implementación en GDevelop

- **Objetos globales** (Ventura, enemigos, proyectiles, efectos, obstáculos, HUD): existen en
  todas las escenas con el mismo nombre.
- **Eventos externos por sistema**: Nivel, Jugador, Combate, Enemigos, Obstáculos, Diálogo,
  Cámara y HUD, más Prólogo y Jefe. Cada escena los enlaza: un cambio en el salto se hace en un
  solo lugar.
- **Grupos**: `Enemigo`, `ProyectilEnemigo`, `Onda`, `Peligro`. Lo común se resuelve una vez sobre
  el grupo.
- **Diálogos como datos**: cada escena guarda su guion en una variable (`Guion`), con líneas
  `Nombre|Texto`.
- Los comentarios de los event sheets explican el porqué de cada estructura no obvia.

**El proyecto se genera desde un script** (`herramientas/construir_juego.py`). Elegimos este camino
para poder regenerar el juego completo de forma reproducible, revisar cada cambio en Git y validar
cada instrucción contra el motor. `juego/game.json` se abre y se juega en el editor; si se lo edita
ahí, el cambio tiene que pasarse al script o se pierde al regenerar.

**Verificación**:
- `validar_eventos.mjs`: cada condición y acción existe, tiene los parámetros correctos y se aplica
  al tipo de objeto correcto. El exportador descarta en silencio las instrucciones inválidas, así
  que sin esto un evento roto no da ningún error.
- `validar_expresiones.mjs`: todas las expresiones con el validador del propio motor.
- `probar_juego.mjs`: carga la exportación en un navegador, aprieta teclas de verdad y registra el
  estado del juego. Incluye un recorrido automático que cruza cada nivel y un seguimiento de la
  máquina de estados del jefe.

### Pruebas (2026-10-11)

| Prueba | Resultado |
|---|---|
| Recorrido automático del prólogo | Llega al nivel 1: diálogos, doble salto y lección de parry |
| Recorrido de los niveles 1, 2 y 3 | Los tres se cruzan completos hasta la escena siguiente |
| Ciclo del jefe | Fases 1 y 2 en el orden del diseño, transición al 50 %, derrota y diálogo final |
| Morir contra el jefe | La pelea se reinicia (320 de vida, fase 1) |
| Menú y capítulos | Navegación con teclado; "La cima de la torre" entra directo a la arena |
| Validadores | Todas las instrucciones y expresiones válidas, sin errores de consola |

---

## Bitácora de decisiones y problemas resueltos

**2026-08-25** — Elegimos GDevelop: gratis, de código abierto y exporta a web sin costo.

**2026-08-28** — Sumamos `gdexporter`, una herramienta de la comunidad para exportar el juego
sin abrir el editor.

**2026-09-01** — Sumamos maná: en la primera versión cargar cartas no costaba nada y se podía
tirar sin pensar.

**2026-09-02** — Revisamos el kit de movimiento: sumamos doble salto y parry porque los pedía un
ataque concreto del jefe (el Aullido se salta, la garra de luna se devuelve). Agacharse se siguió
descartando: ningún ataque lo requiere. Definimos la pelea del jefe por patrones fijos y
extendimos el nivel 1 a un nivel largo con cámara. Problemas resueltos:
- Sprites de Ventura "encimados": las poses de la hoja original se tocaban; pasamos a separarlas
  por componentes conexos.
- Tres animaciones guardadas fuera del arreglo de animaciones del objeto: el JSON era válido pero
  el motor nunca las leía.
- La imagen dejaba de dibujarse al usar `FixCamera`/`ClampCamera`: los límites de cámara pasaron a
  calcularse a mano.
- Auditoría contra la documentación oficial: un jefe "fantasma" (43 eventos y 5 objetos sin
  instancias) que quedaba en el nivel 1 de una prueba anterior.

**2026-10-10 — Rehicimos el proyecto en pixel art.** Para llegar a una entrega profesional
decidimos: juego completo (prólogo, 3 niveles y jefe), pixel art de 48 px, paleta tinta + morado
y resolución 640 × 360. Al reconstruir encontramos que **38 instrucciones del proyecto anterior
eran inválidas** y el exportador las descartaba sin avisar, y que cada escena tenía su propia copia
de la lógica del jugador. Por eso pasamos a generar el proyecto desde un script, con eventos
externos compartidos y validación automática. Ajustamos el salto (se quedaba corto y se repetía
solo al mantener la tecla) y el rebote del toldo (a veces se perdía entre un cuadro y otro
cayendo rápido). Descartamos unos fondos procedurales de edificios genéricos: no eran nuestra
ciudad. Los fondos tienen que salir de nuestras ilustraciones.

**2026-10-11 — Contenido completo.** Sumamos el prólogo, los niveles 2 y 3, la arena del jefe con
sus dos fases, el epílogo con créditos, tres enemigos nuevos (Actor, Cuervo, Agente), péndulos,
retratos de diálogo, menú con capítulos, 41 efectos de sonido y 6 temas. Problemas resueltos:
- **La explosión del farol dañaba en todos los cuadros que duraba** (unas 30 veces 35 de daño).
  Contra los Repintados no se notaba porque morían igual; contra el jefe hubiera sido un golpe
  instantáneo. Ahora daña sólo en el cuadro en que aparece.
- **El menú no resaltaba la opción elegida**: los textos se teñían con la acción de color de los
  Sprite, que el motor ignora en los textos bitmap. Ampliamos el validador para que controle que
  cada instrucción se aplique al tipo de objeto correcto.
- Las líneas largas de diálogo no se cortaban: el texto bitmap sólo ajusta la línea si la
  instancia tiene un ancho propio.
- El logo arrastraba una franja oscura del horizonte del logo original: ahora se recorta siguiendo
  el trazo claro de cada letra.
- El piso de la carpa salía gris, el color de la ciudad de noche: ahora es madera cálida, como el
  resto del recuerdo.
- En algunas hojas el pelaje del lobo salió un tono más claro: se corrige bajando un escalón la
  rampa de grises en esos frames, para que el jefe no cambie de color entre ataques.
