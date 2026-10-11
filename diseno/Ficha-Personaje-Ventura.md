# Ficha de Personaje — Buenaventura "Ventura"

Complementa `GDD.md` y `Guion.md`. Es la referencia visual del protagonista: qué rasgos definen
al personaje y cómo se traducen al sprite de 48 px del juego.

> [!warning] Por qué existe este documento
> El concept art de referencia original tenía la cabeza casi idéntica a **Bendy** (*Bendy and
> the Ink Machine*): orejas curvas tipo cuerno, ojos de botón negros, sonrisa enorme. Esta ficha
> rediseña específicamente esa parte y mantiene todo lo demás (vestuario gótico-victoriano,
> cartas, farol), que sí es propio. Lo necesitábamos para poder defender el diseño como nuestro.

## Qué se mantiene del concept original

- Silueta general: figura alta y angosta, estilo cartoon clásico (rubber-hose).
- Vestuario gótico-victoriano: levita con cola, chaleco de cuello alto, moño, guantes, botas de
  dos tonos.
- Farol antiguo de vidrio esmerilado (prop situacional, no siempre en mano — ver `GDD.md`).
- Paleta: blanco y negro como base, con **morado** como acento (heredado del color de las cartas)
  en vez del verde/azul del concept original.

## Qué cambia (para separarse de Bendy)

| Elemento | Bendy (a evitar) | Ventura (rediseño) |
|---|---|---|
| Orejas/cabeza | Curvas tipo cuerno, puntiagudas | Sin forma de cuerno — un sombrero de ala ancha reemplaza la silueta de la cabeza |
| Ojos | Óvalos negros sólidos, sin pupila visible | Ojos grandes con pupila y ceja visibles — expresivos, no "vacíos" |
| Boca | Sonrisa enorme, todos los dientes | Media sonrisa contenida, de cartomante seguro de sí mismo |
| Accesorio de cabeza | Ninguno (la silueta de las orejas cumple ese rol) | **Sombrero de ala ancha oscuro con un dije de luna creciente en la cinta**: ancla el tema de las cartas y la luna en la silueta |

## Descripción visual de referencia

Joven cartomante *toon*, años 30, línea de tinta negra nítida, casi todo en blanco y negro con
acentos de color limitados. Levita oscura con cola, chaleco crema de cuello alto, moño morado con
un pequeño prendedor de luna, pantalón oscuro, botas victorianas de botones en negro y crema,
guantes blancos. Sombrero de ala ancha con el dije de luna. Cabeza redondeada, ojos ovalados
grandes con pupila y cejas, sonrisa chica y segura, sin orejas en punta. Sostiene un abanico de
cartas moradas con lunas crecientes; el farol de bronce y vidrio cuelga apagado del cinturón.

Referencia aprobada: `diseno/arte/personajes/ventura.jpg` (y `ventura-derrota.jpg`,
`ventura-doble-salto-parry.jpg` para las poses nuevas).

## Del concepto al sprite

- **Tamaño**: 48 px de alto dentro de un lienzo de 96 × 64 (el ancho extra deja lugar al brazo
  extendido de arrojar y a la levita en el salto).
- **Lectura a tamaño real**: a 48 px lo que identifica a Ventura es la silueta del sombrero, la
  cara blanca y las cartas moradas. El contorno de tinta tiene prioridad en el pixelizado: si se
  pierde un píxel de contorno, la silueta deja de leerse.
- **Paleta**: la cerrada del juego (tinta, grises, piel, crema y la rampa de morados).
- **Animaciones**: 18 (idle, correr, salto en cuatro tramos, aterrizaje, doble salto, tres niveles
  de carga, arrojar, lanzar farol, parry, daño, recuperación, derrota, victoria). Ver la sección
  "Medidas del jugador" del GDD.

---

## Ver también

- `GDD.md` — mecánicas, HUD, estructura de niveles.
- `Guion.md` — guion narrativo completo.
