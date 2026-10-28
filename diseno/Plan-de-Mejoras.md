# Plan de mejoras de Toonaria (devolución de la cátedra, octubre 2026)

Devolución recibida del profesor después del Game Test, y lo que hay que presentar en la entrega final según la cátedra (respuesta en el foro, 22/10): **GDD en .doc o .pdf**, **prototipo actualizado en itch.io** y **pitch en video** (mp4 o link a Drive/YouTube). La actividad del campus para subir los entregables todavía no está habilitada.

Fechas del calendario de la carrera: 1.ª entrega **3/11**, 2.ª entrega **10/11**, entrega final **17/11**.

## Devolución, punto por punto

| # | Pedido del profe | Área | Esfuerzo | Entrega |
|---|---|---|---|---|
| 1 | Reconocer si se juega en celular, tablet o PC y mostrar controles táctiles (en el celular hoy no hay controles) | Controles | Medio | 3/11 |
| 2 | Suavizar los movimientos | Game feel | Bajo | 3/11 |
| 3 | Parry más gráfico | Game feel / VFX | Bajo | 3/11 |
| 4 | La recarga tiene que explotar | Game feel / VFX | Bajo | 3/11 |
| 5 | Mejorar la legibilidad de los textos | UI | Bajo | 3/11 |
| 6 | Pantalla de fin de nivel, puntaje y comienzo de la fase siguiente | Flujo / UI | Medio | 3/11 |
| 7 | Mejorar la zona tutorial | Diseño de niveles | Medio | 10/11 |
| 8 | Mejorar la dificultad de los escenarios | Diseño de niveles | Medio | 10/11 |
| 9 | Mapamundi estilo Cuphead, con Ventura recorriendo Toonaria | Escena nueva + arte | Alto | 10/11 |
| 10 | Tienda para comprar mejoras: armas, habilidades, dash, doble dash | Sistemas + economía | Alto | 10/11 |
| 11 | Animación de giro de Ventura al cambiar de dirección | Arte + eventos | Medio | 17/11 |
| 12 | Pulir animaciones y sprites | Arte | Alto | 17/11 |
| 13 | Escenarios más humorísticos: mundo de caricaturas con tono oscuro | Arte + diseño | Alto | 17/11 |
| 14 | Mejorar mucho la historia de Toonaria y el guion | Narrativa | Medio | 17/11 |

## Fase 1: sensación de juego y accesibilidad (para el 3/11) — hecha

Los seis puntos están implementados y probados (ver la bitácora del GDD, 2026-10-23).

1. **Controles táctiles y detección de dispositivo.** Al iniciar cada escena se consulta si el dispositivo es táctil (`SystemInfo::IsMobile()` o el primer toque en pantalla) y, si lo es, se crea una capa de UI con un joystick virtual (izquierda/derecha) y botones de salto, golpe, farol y parry. En PC se ocultan. Los botones tienen que medir al menos 64 px y no tapar la acción. En tablet se escalan según el tamaño de la pantalla.
2. **Movimiento más suave.** Revisar aceleración y desaceleración del comportamiento de plataforma, el seguimiento de la cámara con interpolación y un pequeño margen antes de empezar a seguir (zona muerta).
3. **Parry más gráfico.** Al acertar: *hitstop* de unos 80 ms, destello blanco sobre Ventura, `ParryFx` más grande y con partículas, sacudida corta de cámara y un número o texto «¡PARRY!».
4. **La recarga explota.** Al terminar de recargar el farol: explosión de luz alrededor de Ventura (partículas y flash), sonido propio y empuje o daño en un radio corto a los enemigos cercanos, para que recargar sea una decisión con premio y no una pausa.
5. **Textos legibles.** Fuente bitmap más grande, contorno o sombra de 1 px, fondo semitransparente detrás de los diálogos y velocidad de tipeo ajustable o salteable.
6. **Fin de nivel y puntaje.** Pantalla de resultados al llegar a la meta: tiempo, enemigos vencidos, parries, faroles encendidos y daño recibido → puntaje y calificación (A, B, C). Botones «Siguiente fase» y «Repetir». El puntaje se guarda con almacenamiento persistente.

## Fase 2: estructura de juego (para el 10/11)

7. **Tutorial.** Separar las enseñanzas: una sola mecánica por tramo (moverse, saltar, golpear, parry, farol), con un cartel y un obstáculo seguro para practicar antes de un enemigo real.
8. **Dificultad.** Curva por nivel: cantidad y ubicación de enemigos, puntos de control, vida. Ajustar con los resultados del Game Test (planilla del 19/10).
9. **Mapamundi.** Escena nueva con la ilustración de Toonaria; Ventura camina entre nodos (Prólogo → Nivel 1 → Nivel 2 → Nivel 3 → Torre del jefe → Tienda). Los niveles se desbloquean al completarse y muestran la mejor calificación.
10. **Tienda.** Moneda que se junta en los niveles («chispas» o «tinta»). Tienda con un personaje de Toonaria. Mejoras: **dash**, **doble dash**, más vida, farol más potente, recarga más rápida y un arma alternativa. Las compras se guardan en almacenamiento persistente.

## Fase 3: arte y narrativa (para el 17/11)

11. **Giro de Ventura.** Animación corta de 3 o 4 cuadros al cambiar de dirección (se reproduce una vez y vuelve a correr).
12. **Pulido de sprites.** Revisar todas las animaciones de Ventura y de los enemigos: cuadros intermedios, *anticipation* y *follow-through* en los ataques.
13. **Humor oscuro de caricatura.** Gags de fondo (carteles, personajes de relleno que reaccionan, objetos animados) sin perder el tono sombrío.
14. **Historia.** Reescribir el guion: motivación de Ventura más clara desde el prólogo, Ambrosio como antagonista con un porqué, y escenas cortas entre niveles en el mapamundi.
15. **Entregables finales.** Exportar el GDD a PDF, subir la versión final a itch.io y grabar el pitch en video (1 a 2 minutos: gancho, mecánicas, mundo, cierre).

## Herramientas

- Eventos: cada mejora se valida contra el motor y se prueba jugando antes de exportar.
- Arte nuevo (giro, explosión de la recarga, mapamundi, tienda, íconos de mejoras): mismo proceso de pixelizado y la misma paleta de 20 colores que el resto del juego.
