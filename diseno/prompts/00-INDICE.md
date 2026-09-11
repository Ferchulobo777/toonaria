# Índice de prompts — Toonaria

Cada prompt vive en su propio archivo para pedirlos de a uno. Guardar el resultado en
`Proyecto/diseno/arte/` con el nombre de archivo indicado en cada uno.

## Ya generados y aprobados (quedan acá por si hay que regenerar algo)

| # | Archivo | Qué genera | Estado |
|---|---|---|---|
| 1 | `01-ventura.md` | Personaje jugable, hoja de referencia | ✅ `ventura.jpg` |
| 2 | `02-ambrosio-farolero.md` | Ambrosio, forma humana | ✅ `ambrosio-farolero.jpg` |
| 3 | `03-ambrosio-lobo.md` | Ambrosio, forma jefe (referencia única, no combate) | ✅ `ambrosio-lobo.jpg` |
| 4 | `04-repintado-generico.md` | Enemigo genérico (v2, corregido) | ✅ `repintado-generico.jpg` |
| 5 | `05-carta-luna.md` | Ícono de la carta/proyectil | ✅ `carta-luna.jpg` |
| 6 | `06-nivel1-barrio-reloj.md` | Fondo nivel 1, tramo 1 | ✅ `nivel1-barrio-reloj.jpg` |
| 7 | `07-nivel2-barrio-teatros.md` | Fondo nivel 2 | ✅ `nivel2-barrio-teatros.jpg` (todavía no importado a una escena) |
| 8 | `08-nivel3-corazon-toonaria.md` | Fondo nivel 3 / arena del jefe | ✅ `nivel3-corazon-toonaria.jpg` (todavía no importado a una escena) |
| 9 | `09-logo-toonaria.md` | Logo/key art | ✅ `logo-toonaria.jpg`, en la pantalla de título |
| 10 | `10-ventura-hoja-poses.md` | Hoja de poses de Ventura (idle/carga/correr/salto/combate) | ✅ cubierto por `mov.jpg`, recortado en `arte/ventura-sprites/` |
| 11 | `11-ambrosio-lobo-hoja-combate.md` | Hoja de combate del jefe (5 poses) | ✅ `hoja de combate-lobo.jpg`, recortada en `arte/ambrosio-lobo-sprites/`, importada como el objeto `AmbrosioLobo`. Bonus no pedido: `ambrosio-transformacion-origen.jpg` (secuencia de la transformación original), útil para un flashback que no está en el guión todavía. |
| 12 | `12-farol-bomba-real.md` | Arte real del proyectil farol-bomba | ✅ `farol-bomba-real.jpg`, recortada con transparencia, importada — reemplazó el ícono placeholder que usaba `FarolBomba`. |
| 13 | `13-ambrosio-farolero-hoja-prologo.md` | Hoja de poses de Ambrosio enseñando cartas, para el prólogo | ✅ `ambrosio-farolero-hoja-prologo.jpg` (3 poses: Enseñando/Corrigiendo/Serio), recortadas en `arte/ambrosio-farolero-sprites/` — todavía no importadas a GDevelop porque la escena del prólogo no existe. |
| 14 | `14-ventura-doble-salto-parry.md` | Ventura: poses de doble salto y esquiva/parry | ✅ `ventura-hoja-doble-salto-parry.jpg`, recortada en `ventura-sprites/doble_salto.png` y `parry.png`, importadas como animaciones `SaltoDoble`/`Parry` del objeto `Player`. |
| 15 | `15-ambrosio-lobo-garra-de-luna.md` | Ambrosio Lobo: pose de carga del ataque "Garra de luna" | ✅ `ambrosio-lobo-garra-de-luna.jpg`, recortada e importada como animación `GarraDeLuna`. |
| 16 | `16-proyectil-garra-de-luna.md` | Ícono del proyectil que dispara "Garra de luna" | ✅ `garra-de-luna-proyectil.jpg`, recortado e importado como el objeto `GarraLuna`. |
| 17 | `17-ambrosio-lobo-garra-de-luna-lanzamiento.md` | Ambrosio Lobo: pose de *lanzamiento* del ataque | ✅ 3 variantes generadas — se usó `ambrosio-lobo-garra-de-luna-lanzamiento-v2.jpg` (misma pose que la carga + estallido, mejor continuidad de animación). Las otras 2 quedaron guardadas como alternativas. |
| 18 | `18-ventura-derrota.md` | Ventura: pose de derrota / tirado en el suelo | ✅ `ventura-derrota.jpg`, recortada e importada como animación `Derrota` — reemplazó el placeholder (`RecibirDano` reciclado) en la muerte/respawn. |
| 19 | `19-nivel1-tramo2.md` | Fondo del nivel 1, tramo 2 (x 1280-2560) | ✅ `nivel1-tramo2.jpg`, importada — reemplazó el placeholder que repetía el tramo 1. |
| 20 | `20-nivel1-tramo3.md` | Fondo del nivel 1, tramo 3 (x 2560-3840) | ✅ `nivel1-tramo3.jpg` — la generación original salía con paleta fría (no coincidía con el resto del nivel), se corrigió el tono a cálido con un ajuste de color antes de importar (ver nota abajo). |
| 21 | `21-nivel1-tramo4.md` | Fondo del nivel 1, tramo 4 (x 3840-5120), el límite del barrio | ✅ `nivel1-tramo4.jpg` — mismo ajuste de paleta que el 20. |

> [!info] Nota — ajuste de paleta en los tramos 3 y 4
> Las generaciones de los tramos 3 y 4 salieron con un tono más frío/grisáceo que no coincidía
> con el resto del nivel (que usa luz cálida de farol como fuente principal). Antes de
> importarlas se les aplicó una corrección de color (más cálido, menos azul) para que el
> recorrido se sienta como una sola ciudad y no un color distinto por tramo. Las versiones
> originales (frías) quedaron en `arte/alternos/` por si se prefieren regenerar en vez de
> corregir. También se generó `arte/alternos/nivel1-panoramica-referencia.jpg`, una vista
> panorámica muy angosta que no sirve como fondo de una pantalla (relación de aspecto
> incompatible) — se guarda solo de referencia.

## Pendientes — hacen falta para seguir

Ninguno por ahora. Se van a ir sumando más prompts a medida que haga falta (enemigos nuevos, más
niveles, la arena del jefe, etc.).
