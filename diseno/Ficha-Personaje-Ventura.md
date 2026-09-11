# Ficha de Personaje — Buenaventura "Ventura"

Complementa `GDD.md` y `Guion.md`. Esta ficha es específicamente la referencia visual para
producir sprites — pensada para pegarse tal cual en un generador de imágenes (Nano Banana,
Midjourney, ChatGPT/DALL-E, etc.) o entregarse a quien dibuje.

> [!warning] Por qué existe este documento
> El concept art de referencia original tenía la cabeza casi idéntica a **Bendy** (*Bendy and
> the Ink Machine*) — orejas curvas tipo cuerno, ojos de botón negros, sonrisa enorme. Esta
> ficha rediseña específicamente esa parte, manteniendo todo lo demás (vestuario gótico-
> victoriano, cartas, farol) que sí es propio. Ver el aviso completo en `GDD.md`.

## Qué se mantiene del concept original

- Silueta general: figura alta y angosta, estilo cartoon clásico (rubber-hose).
- Vestuario gótico-victoriano: levita con cola, chaleco de cuello alto, moño, guantes,
  botas de dos tonos.
- Farol antiguo de vidrio esmerilado (prop situacional, no siempre en mano — ver `GDD.md`).
- Paleta: blanco y negro como base, con **morado** como acento (heredado del color de las
  cartas) en vez del verde/azul del concept original.

## Qué cambia (para separarse de Bendy)

| Elemento | Bendy (a evitar) | Ventura (rediseño) |
|---|---|---|
| Orejas/cabeza | Curvas tipo cuerno, puntiagudas | Sin forma de cuerno — silueta redondeada, o un sombrero de ala ancha que reemplaza la silueta de la cabeza por completo |
| Ojos | Óvalos negros sólidos, sin pupila visible | Ojos grandes pero con pupila y ceja visibles — expresivos, no "vacíos" |
| Boca | Sonrisa enorme, todos los dientes, de oreja a oreja | Sonrisa/media sonrisa contenida, de cartomante seguro de sí mismo — no un grito de alegría |
| Accesorio de cabeza | Ninguno (la silueta de las orejas cumple ese rol) | **Sombrero de ala ancha oscuro, con un dije de luna creciente en la cinta** — nuevo elemento, ancla visualmente el tema de las cartas/luna en la silueta |

## Prompt de referencia (para generador de imágenes)

```
Full-body character concept art, 1930s rubber-hose cartoon style (crisp
black ink lineart, mostly black and white with limited color accents),
a confident young male toon fortune-teller named Ventura. Gothic
Victorian wardrobe: dark tailcoat with tails, high-collar cream
waistcoat, deep purple bow tie with a small crescent-moon pin, dark
trousers, two-tone black-and-cream Victorian button boots, white
fingerless gloves. Wide-brimmed dark hat with a thin crescent-moon
charm on the band. Rounded cartoon head, large expressive oval eyes
with visible dark pupils and eyebrows (NOT blank black button eyes), a
small confident smirk (NOT a huge wide open grin), no horn-shaped or
pointed ear silhouettes. Holding a fanned hand of deep purple playing
cards marked with pale crescent-moon symbols. An antique brass-and-
glass Victorian lantern, unlit, clipped to his belt. Full body standing
three-quarter pose, plain flat mid-gray background, clean flat
cel-shaded coloring, character reference sheet style.
```

Sugerencia de relación de aspecto: vertical (3:4 o 2:3) — es una hoja de referencia de cuerpo
completo.

## Próximos pasos de producción (una vez que haya una imagen base aprobada)

1. Confirmar la silueta/cabeza (esta ficha) contra el concept original — ¿se siente todavía
   "el mismo personaje" o hay que ajustar más?
2. A partir de la imagen de referencia aprobada, descomponer en sprite sheet: idle, correr,
   salto, cargar carta (2-3 etapas), arrojar, recibir daño — ver la tabla de frames mínimos en
   la Unidad 2 del vault (`art-and-animation.md` de la skill de proyecto).
3. Definir la resolución base del sprite (ver Unidad 4 del vault — 16×16/32×32/64×64 según el
   nivel de detalle que se busque) antes de producir el resto de las animaciones, para no
   redibujar todo si se cambia después.

---

## Ver también

- `GDD.md` — mecánicas, HUD, estructura de niveles.
- `Guion.md` — guión narrativo completo.
