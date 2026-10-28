"""Arma juego/game.json: objetos, eventos, escenas y niveles de Toonaria.

Arquitectura (para no duplicar lógica entre escenas, que fue el problema de la versión
anterior: Level1 y ArenaJefe tenían cada una su propia copia de todo el jugador):
- Objetos GLOBALES: Ventura, proyectiles, efectos, enemigos, obstáculos, HUD. Existen en todas
  las escenas con el mismo nombre.
- Eventos EXTERNOS por sistema (Jugador, Combate, Enemigos, Obstaculos, Camara, HUD, Dialogo,
  Nivel). Cada escena de juego los enlaza; un cambio en el salto se hace en un solo lugar.
- Cada nivel aporta sólo lo suyo: fondo, tiles, mapa (instancias) y su guion de diálogos.

Los niveles se diseñan como mapas de texto (cada carácter = celda de 16 px), ver NIVELES.

Uso: python herramientas/construir_juego.py
"""

from pathlib import Path

from gd_json import (A, C, E, ENLACE, GRUPO, NOTA, O, PARA_CADA, Recursos, anim, anim_es,
                     anim_termino, al_iniciar, ancho, borrar, cambiar_escena, capa, choca,
                     comparar, comparar_texto, crear, destruir_fuera, escena, escala, externo,
                     frames_de, instancia, mosaico, opacidad, panel, personaje_plataformas,
                     plataforma, si_texto_s, si_var_o, si_var_s, sprite, tam, tamano, tecla,
                     tecla_recien, texto, texto_bitmap, texto_s, una_vez, var_o, var_s,
                     voltear)

RAIZ = Path(__file__).resolve().parents[1]
JUEGO = RAIZ / "juego"
PX = JUEGO / "assets" / "pixel"
W, H = 640, 360
CELDA = 16
DT = "TimeDelta()"
V = "Ventura"
VAR = lambda nombre: f"Ventura.Variable({nombre})"  # noqa: E731

FUENTE = (PX / "fuente" / "toonaria_fuente.fnt", PX / "fuente" / "toonaria_fuente.png")
rec = Recursos(JUEGO)


def efecto_parry():
    """Lo que se ve en todo parry exitoso, sea contra un golpe o contra un proyectil. Se
    exagera a propósito (efecto al doble, destello, fogonazo blanco y cartel) porque es la
    jugada más difícil del juego y tiene que sentirse como un premio, no como un bloqueo."""
    return [crear("ParryFx", f"{V}.X() + {VAR('Mirando')} * 10", f"{V}.Y() - 26"),
            escala("ParryFx", "=", 2),
            crear("Destello", f"{V}.X() + {VAR('Mirando')} * 14", f"{V}.Y() - 26"),
            escala("Destello", "=", 4),
            crear("TextoGolpe", f"{V}.X()", f"{V}.Y() - 64"),
            texto("TextoGolpe", '"¡PARRY!"'),
            A("SetX", "TextoGolpe", "=", f"{V}.X() - TextoGolpe.Width() / 2"),
            var_s("Flash", "=", 0.45)]


def lineas(*renglones):
    """Texto de varias líneas para un parámetro de GDevelop (con NewLine(), no con escapes)."""
    return " + NewLine() + ".join(f'"{r}"' for r in renglones)


def bitmap(nombre, contenido="", escala_=1.0, alinear="left", tinte="255;255;255"):
    return texto_bitmap(rec, nombre, FUENTE[0], FUENTE[1], contenido, escala_, alinear, tinte)


def anims_carpeta(carpeta, especificacion):
    """especificacion: [(nombre_anim, prefijo_archivo, seg_por_frame, bucle)]"""
    return [(n, frames_de(carpeta, p), t, b) for (n, p, t, b) in especificacion]


# =================================================================== OBJETOS GLOBALES

def objetos_globales():
    v = PX / "ventura"
    ventura = sprite(
        rec, V,
        anims_carpeta(v, [
            ("Idle", "Idle", 0.16, True), ("Correr", "Correr", 0.07, True),
            ("SaltoInicio", "SaltoInicio", 0.06, False), ("Subida", "Subida", 0.1, False),
            ("Apice", "Apice", 0.12, False), ("Caida", "Caida", 0.1, True),
            ("Aterrizaje", "Aterrizaje", 0.08, False), ("SaltoDoble", "SaltoDoble", 0.05, False),
            ("Carga1", "Carga1", 0.14, True), ("Carga2", "Carga2", 0.1, True),
            ("CargaCompleta", "CargaCompleta", 0.07, True), ("Arrojar", "Arrojar", 0.07, False),
            ("LanzarFarol", "LanzarFarol", 0.09, False), ("Parry", "Parry", 0.06, False),
            ("RecibirDano", "RecibirDano", 0.1, False), ("Recuperacion", "Recuperacion", 0.2, False),
            ("Derrota", "Derrota", 0.22, False), ("Victoria", "Victoria", 0.3, False)]),
        origen=(48, 62),
        # Caja de colisión angosta (16x40) centrada en el cuerpo: los faldones de la levita y el
        # ala del sombrero son decorativos y no deberían "tocar" pinchos ni enemigos.
        mascara=(40, 22, 56, 62),
        vars_={"Vida": 100, "VidaMax": 100, "Mana": 100, "ManaMax": 100, "Mirando": 1,
               "Carga": 0, "Cargando": 0, "Coyote": 0, "Buffer": 0, "SaltoAereo": 0,
               "EnPisoAntes": 1, "Accion": "", "TiempoAccion": 0, "Invulnerable": 0,
               "Aturdido": 0, "Muerto": 0, "TiempoMuerte": 0, "ParryVentana": 0,
               "ParryCooldown": 0, "FarolCooldown": 0, "SinGastar": 0, "PasoPolvo": 0,
               "EmpujeDir": 1, "Dano": 0, "CargaLista": 0},
        # Aceleración y frenado más bajos que los del comportamiento por defecto: el arranque
        # y la frenada se ven (unos 0,15 s) en vez de ser un corte seco entre quieto y corriendo.
        comportamientos=[personaje_plataformas(acceleration=900, deceleration=1100)])

    p = PX / "proyectiles"
    carta = sprite(rec, "Carta", [(f"Nivel{n}", frames_de(p, f"Carta{n}"), 0.05, True)
                                  for n in (1, 2, 3)],
                   origen=(7, 8), mascara=(2, 2, 12, 14),
                   vars_={"Dano": 10, "Nivel": 1, "Dir": 1, "T": 0},
                   comportamientos=[destruir_fuera()])
    farol = sprite(rec, "FarolBomba", [("Gira", frames_de(p, "FarolBomba"), 0.06, True)],
                   origen=(7, 7), mascara=(2, 2, 12, 12),
                   vars_={"VelX": 0, "VelY": 0, "T": 0}, comportamientos=[destruir_fuera()])

    fx = PX / "fx"
    def efecto(nombre, prefijo, t, origen):
        return sprite(rec, nombre, [("Default", frames_de(fx, prefijo), t, False)], origen=origen,
                      vars_={"Activa": 1})
    efectos = [efecto("Impacto", "Impacto", 0.04, (12, 12)),
               efecto("Explosion", "Explosion", 0.06, (24, 26)),
               efecto("Polvo", "Polvo", 0.07, (10, 9)),
               efecto("Tinta", "Tinta", 0.07, (18, 26)),
               efecto("Destello", "Destello", 0.07, (4, 4)),
               efecto("ParryFx", "Parry", 0.04, (20, 20)),
               efecto("Chispa", "Chispa", 0.04, (6, 6))]
    # La explosión daña por superposición durante su primer cuadro: necesita una caja propia.
    efectos[1]["animations"][0]["directions"][0]["sprites"] = [
        dict(s, hasCustomCollisionMask=True,
             customCollisionMask=[[{"x": 4, "y": 6}, {"x": 44, "y": 6}, {"x": 44, "y": 46},
                                   {"x": 4, "y": 46}]])
        for s in efectos[1]["animations"][0]["directions"][0]["sprites"]]

    # Enemigos. Los cuatro comparten el mismo juego de variables para poder tratarlos como
    # grupo ("Enemigo") en todo lo que es común: recibir cartas y explosiones, el destello del
    # golpe, el daño por contacto y la muerte. Cada uno conserva su propia máquina de estados.
    def enemigo(vida, contacto, vel, rango, estado="patrulla", **extra):
        return dict({"Vida": vida, "VidaMax": vida, "Estado": estado, "T": 0, "Dir": -1,
                     "Izq": 0, "Der": 0, "Rango": rango, "Vel": vel, "Golpe": 0, "Iniciado": 0,
                     "X0": 0, "Y0": 0, "VX": 0, "VY": 0, "Contacto": contacto}, **extra)

    # Mr. Pennypencher, el vecino repintado básico: cuerpo a cuerpo con aviso.
    r = PX / "repintado"
    repintado = sprite(
        rec, "Repintado",
        anims_carpeta(r, [("Idle", "Idle", 0.14, True), ("Caminar", "Caminar", 0.12, True),
                          ("Preparar", "Preparar", 0.2, False), ("Atacar", "Atacar", 0.09, False),
                          ("Golpeado", "Golpeado", 0.1, False), ("Morir", "Morir", 0.1, False)]),
        origen=(32, 62), mascara=(22, 24, 42, 62), vars_=enemigo(30, 8, 30, 64))
    # Actor del barrio de los teatros: ataca a distancia con máscaras que se pueden devolver.
    ac = PX / "actor"
    actor = sprite(
        rec, "Actor",
        anims_carpeta(ac, [("Idle", "Idle", 0.16, True), ("Caminar", "Caminar", 0.13, True),
                           ("Preparar", "Preparar", 1, False), ("Lanzar", "Lanzar", 1, False),
                           ("Recuperar", "Recuperar", 1, False), ("Golpeado", "Golpeado", 0.1, False),
                           ("Morir", "Morir", 0.14, False)]),
        origen=(48, 62), mascara=(40, 14, 56, 62), vars_=enemigo(24, 6, 22, 40))
    # Cuervo de tinta: vuela en su zona y se tira en picada sobre el jugador.
    cu = PX / "cuervo"
    cuervo = sprite(
        rec, "Cuervo",
        anims_carpeta(cu, [("Volar", "Volar", 0.08, True), ("Picada", "Picada", 0.08, False),
                           ("Golpeado", "Golpeado", 0.1, False), ("Morir", "Morir", 0.1, False)]),
        origen=(24, 36), mascara=(16, 28, 34, 44), vars_=enemigo(10, 10, 40, 56, "volar"))
    # Agente: pesado, lento y con casco (las cartas débiles rebotan).
    ag = PX / "agente"
    agente = sprite(
        rec, "Agente",
        anims_carpeta(ag, [("Idle", "Idle", 0.18, True), ("Caminar", "Caminar", 0.15, True),
                           ("Preparar", "Preparar", 0.25, False), ("Golpe", "Golpe", 1, False),
                           ("Golpeado", "Golpeado", 0.12, False), ("Morir", "Morir", 0.12, False)]),
        origen=(56, 70), mascara=(40, 18, 72, 70), vars_=enemigo(70, 12, 20, 56))

    # Proyectiles enemigos: la máscara del Actor y la garra de luna del jefe. Se pueden
    # devolver con parry (Reflejada = 1) y entonces lastiman a quien los tiró.
    mascara_ = sprite(rec, "Mascara", [("Default", frames_de(ac, "Mascara"), 0.07, True)],
                      origen=(8, 8), mascara=(3, 4, 13, 13),
                      vars_={"Dir": 1, "Vel": 150, "T": 0, "Reflejada": 0, "Dano": 12})
    garra = sprite(rec, "GarraLuna", [("Default", frames_de(PX / "proyectiles", "GarraLuna"), 0.06, True)],
                   origen=(10, 8), mascara=(3, 3, 17, 14),
                   vars_={"Dir": 1, "Vel": 210, "T": 0, "Reflejada": 0, "Dano": 18})
    # Ondas a ras del piso: la del garrote del Agente y la del Aullido del jefe (más alta y
    # más larga). Comparten la lógica a través del grupo "Onda".
    onda_suelo = sprite(rec, "OndaSuelo", [("Default", frames_de(PX / "fx", "OndaSuelo"), 0.06, True)],
                        origen=(16, 19), mascara=(4, 9, 28, 19),
                        vars_={"Dir": 1, "T": 0, "Vel": 170, "Duracion": 0.9, "Dano": 14})
    onda_luna = sprite(rec, "OndaLuna", [("Default", frames_de(PX / "fx", "OndaAullido"), 0.07, True)],
                       origen=(24, 39), mascara=(6, 18, 42, 39),
                       vars_={"Dir": 1, "T": 0, "Vel": 190, "Duracion": 2.4, "Dano": 16})

    o = PX / "objetos"
    farol_gas = sprite(rec, "FarolGas",
                       [("Apagado", frames_de(o, "FarolGas_Apagado"), 1, False),
                        ("Encendido", frames_de(o, "FarolGas_Encendido"), 0.12, True)],
                       origen=(12, 59), mascara=(4, 0, 20, 59), vars_={"Encendido": 0})
    te = sprite(rec, "Te", [("Default", frames_de(o, "Te"), 0.3, True)], origen=(7, 15))
    luna = sprite(rec, "Luna", [("Default", frames_de(o, "Luna"), 0.12, True)], origen=(6, 11))
    salida = sprite(rec, "Salida", [("Default", frames_de(o, "Salida"), 1, False)], origen=(24, 71),
                    mascara=(12, 20, 36, 71))

    ob = PX / "obstaculos"
    charco = sprite(rec, "CharcoTinta", [("Default", frames_de(ob, "CharcoTinta"), 0.2, True)],
                    origen=(24, 7), mascara=(4, 3, 44, 8))
    engranaje = sprite(rec, "Engranaje", [("Default", frames_de(ob, "Engranaje"), 0.05, True)],
                       origen=(13, 13), mascara=(4, 4, 22, 22), vars_={"VelY": 0})
    caedor = sprite(rec, "Caedor", [("Default", frames_de(ob, "Engranaje")[:1], 1, False)],
                    origen=(13, 13), vars_={"T": 0, "Periodo": 2.2})
    toldo = sprite(rec, "Toldo",
                   [("Reposo", frames_de(ob, "Toldo_Reposo"), 1, False),
                    ("Aplastado", frames_de(ob, "Toldo_Aplastado"), 1, False),
                    ("Estirado", frames_de(ob, "Toldo_Estirado"), 1, False)],
                   origen=(26, 19), mascara=(3, 6, 49, 19), vars_={"T": 0})
    tablon = sprite(rec, "Tablon",
                    [("Sano", frames_de(ob, "Tablon")[0:1], 1, False),
                     ("Cruje", frames_de(ob, "Tablon")[1:2], 1, False),
                     ("Roto", frames_de(ob, "Tablon")[2:3], 1, False)],
                    origen=(0, 2), mascara=(0, 2, 48, 9),
                    vars_={"Estado": 0, "T": 0, "X0": 0, "Y0": 0, "VelY": 0, "Iniciado": 0},
                    comportamientos=[plataforma()])
    barril = sprite(rec, "Barril",
                    [("Entero", frames_de(ob, "Barril_Entero"), 1, False),
                     ("Roto", frames_de(ob, "Barril_Roto"), 0.08, False)],
                    origen=(11, 25), mascara=(3, 1, 19, 25), vars_={"Roto": 0},
                    comportamientos=[plataforma()])
    andamio = sprite(rec, "Andamio", [("Default", frames_de(ob, "Andamio"), 1, False)],
                     origen=(24, 30), mascara=(0, 30, 48, 36),
                     vars_={"X0": 0, "Y0": 0, "DX": 80, "DY": 0, "Vel": 1.2, "Fase": 0,
                            "Iniciado": 0},
                     comportamientos=[plataforma("Jumpthru")])
    nube = sprite(rec, "NubeTinta", [("Default", frames_de(ob, "NubeTinta"), 0.5, True)],
                  origen=(24, 8), mascara=(4, 6, 44, 12),
                  vars_={"X0": 0, "Y0": 0, "DX": 0, "DY": 28, "Vel": 1.0, "Fase": 0,
                         "Iniciado": 0},
                  comportamientos=[plataforma("Jumpthru")])
    rejas = mosaico(rec, "Rejas", ob / "Rejas.png", 32, 20)
    # Péndulo (bolsa de arena de la tramoya): gira alrededor del eje de arriba, así que el
    # origen y el centro de rotación están en el gancho y la caja de colisión sólo en el peso.
    pendulo = sprite(rec, "Pendulo", [("Default", frames_de(ob, "Pendulo"), 1, False)],
                     origen=(18, 2), centro=(18, 2), mascara=(4, 84, 32, 110),
                     vars_={"Amplitud": 55, "Vel": 1.6, "Fase": 0})
    zarpazo = sprite(rec, "Zarpazo", [("Default", frames_de(fx, "Impacto"), 0.05, False)],
                     origen=(12, 12))

    h = PX / "hud"
    hud = [
        sprite(rec, "Retrato", [("Default", frames_de(h, "Retrato"), 1, False)], origen=(0, 0)),
        sprite(rec, "CartaVida",
               [(e, frames_de(h, f"CartaVida_{e}"), 1, False) for e in ("Llena", "Media", "Vacia")],
               origen=(0, 0), vars_={"Indice": 0}),
        sprite(rec, "BarraManaFondo", [("Default", frames_de(h, "BarraManaFondo"), 1, False)],
               origen=(0, 0)),
        sprite(rec, "BarraMana", [("Default", frames_de(h, "BarraMana"), 1, False)], origen=(0, 0)),
        sprite(rec, "BarraCargaFondo", [("Default", frames_de(h, "BarraCargaFondo"), 1, False)],
               origen=(12, 2)),
        sprite(rec, "BarraCarga", [(f"Nivel{n}", [h / f"BarraCarga_{n}.png"], 1, False)
                                   for n in (1, 2, 3)], origen=(0, 1)),
        sprite(rec, "Negro", [("Default", [h / "Negro.png"], 1, False)], origen=(0, 0)),
        panel(rec, "CajaDialogo", h / "CajaDialogo.png", 600, 76, 6),
        sprite(rec, "Seguir", [("Default", frames_de(h, "Seguir"), 1, False)], origen=(3, 2)),
        sprite(rec, "RetratoDialogo",
               [("Ventura", frames_de(h, "Retrato"), 1, False)]
               + [(n, frames_de(h, f"Retrato{n}"), 1, False) for n in ("Ambrosio", "Actor", "Lobo")],
               origen=(0, 0)),
        bitmap("TextoDialogo"), bitmap("NombreDialogo", tinte="176;133;214"),
        bitmap("TextoAviso", alinear="center"), bitmap("TextoPausa", escala_=2.0, alinear="center"),
    ]
    zona = sprite(rec, "ZonaDialogo", [("Default", [h / "Negro.png"], 1, False)], origen=(0, 0),
                  vars_={"Id": "", "Visto": 0, "Despues": ""})
    # Controles táctiles: un solo objeto con una animación por botón; cada instancia dice en
    # Tipo qué acción representa, y así la lectura de los toques es la misma para todos.
    tactil = h / "tactil"
    botones = sprite(rec, "BotonTactil",
                     [(n, frames_de(tactil, f"Boton{n}"), 1, False)
                      for n in ("Izq", "Der", "Saltar", "Carta", "Farol", "Parry", "Pausa")],
                     origen=(0, 0), vars_={"Tipo": ""})
    extras = [
        botones,
        sprite(rec, "Blanco", [("Default", [h / "Blanco.png"], 1, False)], origen=(0, 0)),
        bitmap("TextoGolpe", alinear="center", tinte="238;226;246"),
        panel(rec, "FondoAviso", h / "CajaDialogo.png", 200, 20, 6),
        bitmap("TituloResultados", escala_=2.0, alinear="center", tinte="246;199;96"),
        bitmap("TextoResultados"),
    ]
    return ([ventura, carta, farol] + efectos + [repintado, actor, cuervo, agente, mascara_, garra,
            onda_suelo, onda_luna, farol_gas, te, luna, salida, charco, engranaje, caedor, toldo, tablon,
            barril, andamio, nube, rejas, pendulo, zarpazo, zona] + hud + extras)


def grupo(nombre, *objetos):
    return {"name": nombre, "objects": [{"name": o} for o in objetos]}


GRUPOS_GLOBALES = [
    grupo("Peligro", "CharcoTinta", "Rejas", "Engranaje", "Pendulo"),
    grupo("Enemigo", "Repintado", "Actor", "Cuervo", "Agente"),
    grupo("ProyectilEnemigo", "Mascara", "GarraLuna"),
    grupo("Onda", "OndaSuelo", "OndaLuna"),
]


# =================================================================== EVENTOS: JUGADOR

def plat(tipo, *extra, neg=False):
    return C(f"PlatformBehavior::{tipo}", V, "PlatformerObject", *extra, neg=neg)


def plat_a(tipo, *extra):
    return A(f"PlatformBehavior::{tipo}", V, "PlatformerObject", *extra)


SALTO = ("Space", "w", "Up")


def tactil(boton):
    """El botón táctil está apretado (lo mantiene la hoja Tactil en Tactil.<boton>)."""
    return si_var_s(f"Tactil.{boton}", "=", 1)


def tactil_recien(boton):
    """El botón táctil se apretó en este cuadro (equivale a 'tecla recién presionada')."""
    return si_var_s(f"Tactil.{boton}Recien", "=", 1)


def recien_salto():
    return O(*[tecla_recien(k) for k in SALTO], tactil_recien("Saltar"))


BOTONES_TACTILES = ("Izq", "Der", "Saltar", "Carta", "Farol", "Parry", "Pausa")

LEER_TOQUES = """// Leo todos los toques activos y no sólo el primero: con el cursor simulado por el toque
// no se podría mantener una flecha y saltar al mismo tiempo. Cada botón queda apretado si
// algún toque cae dentro de su caja, y "Recien" vale 1 sólo en el cuadro en que se apretó.
const estado = runtimeScene.getVariables().get("Tactil");
const entrada = runtimeScene.getGame().getInputManager();
const capa = runtimeScene.getLayer("Tactil");
const toques = entrada.getAllTouchIdentifiers();
for (const boton of runtimeScene.getObjects("BotonTactil")) {
  const tipo = boton.getVariables().get("Tipo").getAsString();
  let apretado = false;
  for (const id of toques) {
    const punto = capa.convertCoords(entrada.getTouchX(id), entrada.getTouchY(id));
    if (boton.insideObject(punto[0], punto[1])) {
      apretado = true;
      break;
    }
  }
  const antes = estado.getChild(tipo).getAsNumber();
  estado.getChild(tipo + "Recien").setNumber(apretado && antes === 0 ? 1 : 0);
  estado.getChild(tipo).setNumber(apretado ? 1 : 0);
  boton.setOpacity(apretado ? 255 : 140);
}"""


def codigo_js(codigo):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": codigo,
            "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}


def eventos_tactil():
    return [
        GRUPO("Controles táctiles", [
            NOTA("Los botones en pantalla aparecen sólo si el dispositivo tiene pantalla táctil "
                 "(celular o tablet), o apenas alguien toca la pantalla. En una PC con teclado "
                 "no tapan nada. Como el juego se escala entero a la pantalla, los botones "
                 "crecen solos en una tablet."),
            E([al_iniciar()], [A("HideLayer", "", '"Tactil"'),
                               A("AnimatableCapability::AnimatableBehavior::SetName", "BotonTactil",
                                 "Animation", "=", "BotonTactil.VariableString(Tipo)")]),
            E([al_iniciar(), C("SystemInfo::HasTouchScreen", "")],
              [A("ShowLayer", "", '"Tactil"')]),
            E([C("HasAnyTouchStarted", "")], [A("ShowLayer", "", '"Tactil"')]),
            codigo_js(LEER_TOQUES),
        ], color="jugador"),
    ]


def eventos_jugador():
    vy = (f"({V}.PlatformerObject::CurrentFallSpeed() - "
          f"{V}.PlatformerObject::CurrentJumpSpeed())")
    libre = [si_var_s("Bloqueado", "=", 0), si_var_o(V, "Muerto", "=", 0)]
    return [
        GRUPO("Temporizadores del jugador", [
            NOTA("Todos los tiempos del personaje bajan juntos acá. Se usan variables en vez "
                 "de los temporizadores del motor para que la pausa y la cámara lenta del "
                 "golpe (TimeDelta escalado) los afecten de la misma forma."),
            E([], [var_o(V, n, "-", DT) for n in
                   ("TiempoAccion", "Invulnerable", "Aturdido", "ParryVentana", "ParryCooldown",
                    "FarolCooldown", "PasoPolvo", "Coyote", "Buffer")]
              + [var_o(V, "SinGastar", "+", DT)]),
        ]),
        GRUPO("Control y bloqueo", [
            NOTA("El jugador pierde el control en tres casos: diálogo/transición (Bloqueado), "
                 "aturdido por un golpe (para que el empuje no lo pise la tecla) y muerto."),
            E([O(si_var_s("Bloqueado", "=", 1), si_var_o(V, "Aturdido", ">", 0),
                 si_var_o(V, "Muerto", "=", 1))],
              [plat_a("IgnoreDefaultControls", "yes")]),
            E([si_var_s("Bloqueado", "=", 0), si_var_o(V, "Aturdido", "<=", 0),
               si_var_o(V, "Muerto", "=", 0)],
              [plat_a("IgnoreDefaultControls", "no")],
              [E([O(tecla("a"), tecla("Left"), tactil("Izq"))], [plat_a("SimulateLeftKey")]),
               E([O(tecla("d"), tecla("Right"), tactil("Der"))], [plat_a("SimulateRightKey")]),
               NOTA("W, flecha arriba y el botón táctil saltan igual que Espacio. Simular la "
                    "tecla mientras se mantiene apretada también sostiene el salto (salto "
                    "variable)."),
               E([O(tecla("w"), tecla("Up"), tactil("Saltar"))], [plat_a("SimulateJumpKey")])]),
            E(libre + [si_var_o(V, "Aturdido", "<=", 0), O(tecla("a"), tecla("Left"), tactil("Izq"))],
              [var_o(V, "Mirando", "=", -1), voltear(V, True)]),
            E(libre + [si_var_o(V, "Aturdido", "<=", 0), O(tecla("d"), tecla("Right"), tactil("Der"))],
              [var_o(V, "Mirando", "=", 1), voltear(V, False)]),
        ]),
        GRUPO("Sensación de salto", [
            NOTA("Gravedad asimétrica: sube con 1200 y cae con 1600, así el personaje no 'flota' "
                 "al bajar. Ojo con el modelo del motor: durante la subida la velocidad de salto "
                 "baja con la gravedad Y la de caída sube con la gravedad, o sea que se frena "
                 "con el doble. Con velocidad de salto 427 y sostén de 0,3 s queda un salto "
                 "corto de ~38 px (tocar) y uno completo de ~75 px (mantener)."),
            E([plat("IsFalling")], [plat_a("Gravity", "=", 1600)]),
            E([plat("IsFalling", neg=True)], [plat_a("Gravity", "=", 1200)]),
            NOTA("Cargar una carta frena: tirar fuerte tiene que costar movilidad."),
            E([si_var_o(V, "Cargando", "=", 1)], [plat_a("MaxSpeed", "=", 90)]),
            E([si_var_o(V, "Cargando", "=", 0)], [plat_a("MaxSpeed", "=", 150)]),
            E([plat("IsOnFloor")],
              [var_o(V, "Coyote", "=", 0.1), var_o(V, "SaltoAereo", "=", 0),
               plat_a("JumpSpeed", "=", 427)]),
            NOTA("Doble salto (anula la velocidad de caída, así rinde igual aunque se use bajando). "
                 "Va ANTES del 'coyote time' a propósito: si el coyote dispara en "
                 "este mismo cuadro pone Coyote en 0, y este evento ya se evaluó con Coyote > 0, "
                 "así una sola pulsación nunca gasta los dos saltos."),
            E(libre + [plat("IsOnFloor", neg=True), si_var_o(V, "Coyote", "<=", 0),
                       si_var_o(V, "SaltoAereo", "=", 0), recien_salto()],
              [A("PlatformBehavior::PlatformerObjectBehavior::SetCurrentFallSpeed", V, "PlatformerObject", "=", 0), plat_a("SetCanJump"), plat_a("SimulateJumpKey"),
               var_o(V, "SaltoAereo", "=", 1),
               A("SetStringObjectVariable", V, "Accion", "=", '"SaltoDoble"'),
               var_o(V, "TiempoAccion", "=", 0.3),
               crear("Destello", f"{V}.X()", f"{V}.Y()"), sonido_fx("salto_doble")]),
            NOTA("Coyote time: 0,1 s de gracia para saltar después de pisar el vacío. Sin esto "
                 "el jugador siente que apretó a tiempo y el juego 'no le hizo caso'."),
            E(libre + [plat("IsOnFloor", neg=True), plat("IsJumping", neg=True),
                       si_var_o(V, "Coyote", ">", 0), recien_salto()],
              [plat_a("SetCanJump"), plat_a("SimulateJumpKey"), var_o(V, "Coyote", "=", 0)]),
            NOTA("Buffer de salto: si se aprieta saltar poco antes de tocar el piso, el salto "
                 "sale igual al aterrizar."),
            E([plat("IsOnFloor", neg=True), recien_salto()], [var_o(V, "Buffer", "=", 0.12)]),
            E(libre + [plat("IsOnFloor"), si_var_o(V, "Buffer", ">", 0)],
              [plat_a("SimulateJumpKey"), var_o(V, "Buffer", "=", 0)]),
            E(libre + [plat("IsOnFloor"), recien_salto()], [sonido_fx("salto")]),
        ]),
        GRUPO("Aterrizaje y polvo", [
            E([plat("IsOnFloor"), si_var_o(V, "EnPisoAntes", "=", 0)],
              [crear("Polvo", f"{V}.X()", f"{V}.Y()"), sonido_fx("aterrizar", 40)],
              [E([si_var_o(V, "TiempoAccion", "<=", 0)],
                 [A("SetStringObjectVariable", V, "Accion", "=", '"Aterrizaje"'),
                  var_o(V, "TiempoAccion", "=", 0.08)])]),
            E([plat("IsOnFloor"), C("PlatformBehavior::PlatformerObjectBehavior::IsMovingEvenALittle",
                                    V, "PlatformerObject"), si_var_o(V, "PasoPolvo", "<=", 0)],
              [crear("Polvo", f"{V}.X() - {VAR('Mirando')} * 8", f"{V}.Y()"),
               escala("Polvo", "=", 0.6), var_o(V, "PasoPolvo", "=", 0.28)]),
            E([plat("IsOnFloor")], [var_o(V, "EnPisoAntes", "=", 1)]),
            E([plat("IsOnFloor", neg=True)], [var_o(V, "EnPisoAntes", "=", 0)]),
        ]),
        GRUPO("Animación", [
            NOTA("Una sola máquina de estados de animación, por prioridad: primero la base "
                 "(piso/aire), después la carga, después las acciones puntuales (arrojar, "
                 "parry, golpe, que duran TiempoAccion) y por último la muerte. Cada evento "
                 "pisa al anterior, así que el orden ES la prioridad."),
            E([plat("IsOnFloor"),
               C("PlatformBehavior::PlatformerObjectBehavior::IsMovingEvenALittle", V,
                 "PlatformerObject")], [anim(V, "Correr")]),
            E([plat("IsOnFloor"),
               C("PlatformBehavior::PlatformerObjectBehavior::IsMovingEvenALittle", V,
                 "PlatformerObject", neg=True)], [anim(V, "Idle")]),
            E([plat("IsOnFloor", neg=True), comparar(vy, "<", -90)], [anim(V, "Subida")]),
            E([plat("IsOnFloor", neg=True), comparar(vy, ">=", -90), comparar(vy, "<=", 90)],
              [anim(V, "Apice")]),
            E([plat("IsOnFloor", neg=True), comparar(vy, ">", 90)], [anim(V, "Caida")]),
            E([si_var_o(V, "Cargando", "=", 1), si_var_o(V, "Carga", "<", 45)],
              [anim(V, "Carga1")]),
            E([si_var_o(V, "Cargando", "=", 1), si_var_o(V, "Carga", ">=", 45),
               si_var_o(V, "Carga", "<", 90)], [anim(V, "Carga2")]),
            E([si_var_o(V, "Cargando", "=", 1), si_var_o(V, "Carga", ">=", 90)],
              [anim(V, "CargaCompleta")]),
            E([si_var_o(V, "TiempoAccion", ">", 0)],
              [A("AnimatableCapability::AnimatableBehavior::SetName", V, "Animation", "=",
                 f"{V}.VariableString(Accion)")]),
            E([si_var_o(V, "Muerto", "=", 1)], [anim(V, "Derrota")]),
            NOTA("Parpadeo de invulnerabilidad: el jugador tiene que VER que no lo pueden "
                 "golpear de nuevo durante ese segundo."),
            E([si_var_o(V, "Invulnerable", ">", 0), si_var_o(V, "Muerto", "=", 0)],
              [opacidad(V, "=", f"255 - 175 * mod(floor({VAR('Invulnerable')} * 16), 2)")]),
            E([si_var_o(V, "Invulnerable", "<=", 0)], [opacidad(V, "=", 255)]),
        ], color="jugador"),
    ]


def sonido_fx(nombre, volumen=60):
    ruta = JUEGO / "assets" / "sonido" / f"{nombre}.wav"
    if not ruta.exists():
        return A("SetNumberVariable", "SinSonido", "=", 0)
    return A("PlaySound", "", rec.audio(ruta), "no", volumen, 1)


def musica(nombre, volumen=45):
    """La música va siempre por el canal 1: tocar otro tema en el mismo canal reemplaza al
    anterior, así el cambio de escena no deja dos temas sonando a la vez."""
    ruta = JUEGO / "assets" / "musica" / f"{nombre}.ogg"
    return A("PlayMusicOnChannel", "", rec.audio(ruta, musica=True), 1, "yes", volumen, 1)


def parar_musica():
    return A("StopMusicCanal", "", 1)


# =================================================================== EVENTOS: COMBATE

def eventos_combate():
    libre = [si_var_s("Bloqueado", "=", 0), si_var_o(V, "Muerto", "=", 0)]
    teclas_carta = O(tecla_recien("x"), tecla_recien("j"), tactil_recien("Carta"))
    return [
        GRUPO("Maná", [
            NOTA("El maná se recupera recién después de 0,9 s sin gastar: obliga a elegir "
                 "entre seguir tirando débil o parar a recargar."),
            E([si_var_o(V, "SinGastar", ">=", 0.9), si_var_o(V, "Mana", "<", f"{VAR('ManaMax')}")],
              [var_o(V, "Mana", "+", f"22 * {DT}")]),
            E([si_var_o(V, "Mana", ">", f"{VAR('ManaMax')}")],
              [var_o(V, "Mana", "=", f"{VAR('ManaMax')}")]),
        ], color="combate"),
        GRUPO("Carta lunar (cargar y soltar)", [
            E(libre + [teclas_carta, si_var_o(V, "Cargando", "=", 0), si_var_o(V, "Mana", ">=", 4)],
              [var_o(V, "Cargando", "=", 1), var_o(V, "Carga", "=", 0), sonido_fx("carga", 35)]),
            E([si_var_o(V, "Cargando", "=", 1), O(tecla("x"), tecla("j"), tactil("Carta"))],
              [var_o(V, "Carga", "=", f"min(100, {VAR('Carga')} + 150 * {DT})")]),
            NOTA("Cuando la carga llega al máximo hay un estallido de luz alrededor de Ventura: "
                 "el jugador tiene que saber, sin mirar el medidor, que la carta ya explota."),
            E([si_var_o(V, "Cargando", "=", 1), si_var_o(V, "Carga", ">=", 90),
               si_var_o(V, "CargaLista", "=", 0)],
              [var_o(V, "CargaLista", "=", 1),
               crear("Destello", f"{V}.X()", f"{V}.Y() - 30"), escala("Destello", "=", 3),
               crear("Chispa", f"{V}.X() - 10", f"{V}.Y() - 40"),
               crear("Chispa", f"{V}.X() + 10", f"{V}.Y() - 20"),
               var_s("Flash", "=", 0.25), var_s("Temblor", "=", 1.5), sonido_fx("garra_carga", 45)]),
            E([si_var_o(V, "Cargando", "=", 0)], [var_o(V, "CargaLista", "=", 0)]),
            NOTA("Soltar: el daño, la velocidad y el costo escalan con la carga. Nivel de la "
                 "carta = 1 + floor(Carga/45): de 0 a 44 débil, de 45 a 89 media, 90 o más "
                 "completa (la animación de la carta cambia con el nivel)."),
            E([si_var_o(V, "Cargando", "=", 1), tecla("x", neg=True), tecla("j", neg=True),
               si_var_s("Tactil.Carta", "=", 0)],
              [crear("Carta", f"{V}.X() + {VAR('Mirando')} * 16", f"{V}.Y() - 30"),
               var_o("Carta", "Nivel", "=", f"min(3, 1 + floor({VAR('Carga')} / 45))"),
               var_o("Carta", "Dano", "=", f"round(8 + {VAR('Carga')} * 0.32)"),
               var_o("Carta", "Dir", "=", VAR("Mirando")),
               A("AnimatableCapability::AnimatableBehavior::SetName", "Carta", "Animation", "=",
                 '"Nivel" + ToString(Carta.Variable(Nivel))'),
               A("AddForceXY", "Carta", f"{VAR('Mirando')} * (300 + {VAR('Carga')} * 1.5)", 0, 1),
               var_o(V, "Mana", "-", f"min({VAR('Mana')}, 4 + {VAR('Carga')} * 0.16)"),
               var_o(V, "SinGastar", "=", 0), var_o(V, "Cargando", "=", 0),
               var_o(V, "Carga", "=", 0),
               A("SetStringObjectVariable", V, "Accion", "=", '"Arrojar"'),
               var_o(V, "TiempoAccion", "=", 0.22), sonido_fx("carta")]),
            E([], [var_o("Carta", "T", "+", DT)]),
            E([si_var_o("Carta", "T", ">", 1.2)], [borrar("Carta")]),
            NOTA("La carta cargada al máximo (nivel 3) explota al chocar: usa la misma "
                 "Explosion del farol, así el daño en área ya está resuelto para enemigos y "
                 "barriles. El premio de esperar la carga completa es poder pegarle a un grupo."),
            E([choca("Carta", "Suelo"), si_var_o("Carta", "Nivel", "=", 3)],
              [crear("Explosion", "Carta.X()", "Carta.Y()"), var_s("Temblor", "=", 5),
               sonido_fx("explosion", 65)]),
            E([choca("Carta", "Suelo")],
              [crear("Impacto", "Carta.X()", "Carta.Y()"), borrar("Carta")]),
        ], color="combate"),
        GRUPO("Farol incendiario", [
            NOTA("El farol de Ambrosio como granada: no se carga, sale en arco (velocidad "
                 "vertical inicial + gravedad propia) y explota en área. Cuesta 30 de maná."),
            E(libre + [O(tecla_recien("c"), tecla_recien("k"), tactil_recien("Farol")),
                       si_var_o(V, "FarolCooldown", "<=", 0), si_var_o(V, "Mana", ">=", 30),
                       si_var_o(V, "Cargando", "=", 0)],
              [crear("FarolBomba", f"{V}.X() + {VAR('Mirando')} * 12", f"{V}.Y() - 32"),
               var_o("FarolBomba", "VelX", "=", f"{VAR('Mirando')} * 170"),
               var_o("FarolBomba", "VelY", "=", -240),
               var_o(V, "Mana", "-", 30), var_o(V, "SinGastar", "=", 0),
               var_o(V, "FarolCooldown", "=", 0.8),
               A("SetStringObjectVariable", V, "Accion", "=", '"LanzarFarol"'),
               var_o(V, "TiempoAccion", "=", 0.3), sonido_fx("farol")]),
            E([], [var_o("FarolBomba", "VelY", "+", f"700 * {DT}"),
                   var_o("FarolBomba", "T", "+", DT),
                   A("SetX", "FarolBomba", "+", f"FarolBomba.Variable(VelX) * {DT}"),
                   A("SetY", "FarolBomba", "+", f"FarolBomba.Variable(VelY) * {DT}")]),
            E([O(choca("FarolBomba", "Suelo"), choca("FarolBomba", "Enemigo"),
                 choca("FarolBomba", "Barril"), si_var_o("FarolBomba", "T", ">", 2.5))],
              [crear("Explosion", "FarolBomba.X()", "FarolBomba.Y()"),
               var_s("Temblor", "=", 5), borrar("FarolBomba"), sonido_fx("explosion", 70)]),
            E([anim_termino("Explosion")], [borrar("Explosion")]),
        ], color="combate"),
        GRUPO("Parry", [
            NOTA("Ventana corta (0,2 s) y enfriamiento (0,45 s): el parry es una apuesta de "
                 "timing, no un escudo que se pueda mantener apretado."),
            E(libre + [O(tecla_recien("z"), tecla_recien("l"), tactil_recien("Parry")),
                       si_var_o(V, "ParryCooldown", "<=", 0)],
              [var_o(V, "ParryVentana", "=", 0.2), var_o(V, "ParryCooldown", "=", 0.45),
               var_o(V, "Cargando", "=", 0),
               A("SetStringObjectVariable", V, "Accion", "=", '"Parry"'),
               var_o(V, "TiempoAccion", "=", 0.3), sonido_fx("parry_aire", 40)]),
        ], color="combate"),
        GRUPO("Recibir daño", [
            NOTA("Todo lo que lastima carga Ventura.Dano y EmpujeDir; el daño se aplica en un "
                 "solo evento al final. Así la invulnerabilidad, el empuje, el temblor y la "
                 "cámara lenta del golpe son idénticos venga de donde venga."),
            E([si_var_o(V, "Invulnerable", "<=", 0), si_var_o(V, "Muerto", "=", 0),
               si_var_o(V, "ParryVentana", "<=", 0), choca(V, "Peligro")],
              [var_o(V, "Dano", "=", 12), var_o(V, "EmpujeDir", "=", f"-{VAR('Mirando')}")]),
            E([si_var_o(V, "Dano", ">", 0)],
              [var_o(V, "Vida", "-", VAR("Dano")), var_s("DanoRecibido", "+", VAR("Dano")),
               var_o(V, "Invulnerable", "=", 1.0),
               var_o(V, "Aturdido", "=", 0.22), var_o(V, "Cargando", "=", 0),
               A("SetStringObjectVariable", V, "Accion", "=", '"RecibirDano"'),
               var_o(V, "TiempoAccion", "=", 0.35),
               A("PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed", V,
                 "PlatformerObject", "=", f"{VAR('EmpujeDir')} * 170"),
               var_s("Temblor", "=", 4), var_s("Hitstop", "=", 4),
               crear("Chispa", f"{V}.X()", f"{V}.Y() - 26"), sonido_fx("dano"),
               var_o(V, "Dano", "=", 0)]),
        ], color="combate"),
        GRUPO("Muerte, caída y reaparición", [
            E([si_var_o(V, "Vida", "<=", 0), si_var_o(V, "Muerto", "=", 0)],
              [var_o(V, "Muerto", "=", 1), var_o(V, "TiempoMuerte", "=", 0),
               var_o(V, "Cargando", "=", 0), var_s("Temblor", "=", 6), sonido_fx("derrota")]),
            E([si_var_o(V, "Muerto", "=", 1)], [var_o(V, "TiempoMuerte", "+", DT)]),
            E([si_var_o(V, "Muerto", "=", 1), si_var_o(V, "TiempoMuerte", ">=", 1.5)],
              [var_s("FundidoObjetivo", "=", 1)]),
            NOTA("Reaparece en el último farol encendido con todo recargado: el castigo de "
                 "morir es perder el tramo recorrido, no los recursos."),
            E([si_var_o(V, "Muerto", "=", 1), si_var_o(V, "TiempoMuerte", ">=", 2.1)],
              [A("SetXY", V, "=", "Variable(CheckX)", "=", "Variable(CheckY)"),
               var_o(V, "Vida", "=", VAR("VidaMax")), var_o(V, "Mana", "=", VAR("ManaMax")),
               var_o(V, "Muerto", "=", 0), var_o(V, "Invulnerable", "=", 1.5),
               A("PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed", V,
                 "PlatformerObject", "=", 0),
               var_s("CamX", "=", f"{V}.X()"), var_s("CamY", "=", f"{V}.Y() - 40"),
               var_s("FundidoObjetivo", "=", 0)]),
            NOTA("Caer a un precipicio cuesta 25 de vida y devuelve al último farol con un "
                 "fundido rápido, sin la animación de derrota (no hay cuerpo que mostrar)."),
            E([C("PosY", V, ">", "Variable(NivelAlto) + 40"), si_var_o(V, "Muerto", "=", 0)],
              [var_o(V, "Vida", "-", 25),
               A("SetXY", V, "=", "Variable(CheckX)", "=", "Variable(CheckY)"),
               A("PlatformBehavior::PlatformerObjectBehavior::SetCurrentFallSpeed", V,
                 "PlatformerObject", "=", 0),
               var_o(V, "Invulnerable", "=", 1.2), var_s("Fundido", "=", 1),
               var_s("CamX", "=", f"{V}.X()"), var_s("CamY", "=", f"{V}.Y() - 40"),
               sonido_fx("caida")]),
        ], color="combate"),
        GRUPO("Cámara lenta del golpe (hitstop)", [
            NOTA("Se cuenta en cuadros y no en segundos: con la escala de tiempo en 0,05 "
                 "TimeDelta casi no avanza y un temporizador en segundos nunca terminaría."),
            E([si_var_s("Hitstop", ">", 0)],
              [A("ChangeTimeScale", "", 0.05), var_s("Hitstop", "-", 1)]),
            E([si_var_s("Hitstop", "<=", 0), si_var_s("Pausa", "=", 0)],
              [A("ChangeTimeScale", "", 1)]),
        ], color="combate"),
    ]


# =================================================================== EVENTOS: ENEMIGOS

def estado_es(obj, nombre, neg=False):
    return si_texto_o(obj, "Estado", "!=" if neg else "=", f'"{nombre}"')


def poner_estado(obj, nombre):
    return A("SetStringObjectVariable", obj, "Estado", "=", f'"{nombre}"')


def en_rango(obj, dx, dy_arriba, dy_abajo=None):
    """Condiciones que eligen las instancias de obj cerca de Ventura (por instancia, con PosX y
    PosY: una comparación de números suelta usaría siempre la primera instancia)."""
    dy_abajo = dy_arriba if dy_abajo is None else dy_abajo
    return [C("PosX", obj, ">", f"{V}.X() - {dx}"), C("PosX", obj, "<", f"{V}.X() + {dx}"),
            C("PosY", obj, ">", f"{V}.Y() - {dy_abajo}"), C("PosY", obj, "<", f"{V}.Y() + {dy_arriba}"),
            si_var_o(V, "Muerto", "=", 0)]


def patrulla(obj, anim_caminar="Caminar"):
    return [
        E([si_var_o(obj, "Iniciado", "=", 0)],
          [var_o(obj, "Izq", "=", f"{obj}.X() - {obj}.Variable(Rango)"),
           var_o(obj, "Der", "=", f"{obj}.X() + {obj}.Variable(Rango)"),
           var_o(obj, "X0", "=", f"{obj}.X()"), var_o(obj, "Y0", "=", f"{obj}.Y()"),
           var_o(obj, "Iniciado", "=", 1)]),
        E([estado_es(obj, "patrulla")],
          [A("SetX", obj, "+", f"{obj}.Variable(Dir) * {obj}.Variable(Vel) * {DT}"),
           anim(obj, anim_caminar)]),
        E([estado_es(obj, "patrulla"), C("PosX", obj, "<", f"{obj}.Variable(Izq)")],
          [var_o(obj, "Dir", "=", 1)]),
        E([estado_es(obj, "patrulla"), C("PosX", obj, ">", f"{obj}.Variable(Der)")],
          [var_o(obj, "Dir", "=", -1)]),
    ]


def cuenta_regresiva(obj, estado, siguiente, t_siguiente, acciones=()):
    """Estado temporizado: baja T y al llegar a 0 pasa al siguiente."""
    return [
        E([estado_es(obj, estado)], [var_o(obj, "T", "-", DT)]),
        E([estado_es(obj, estado), si_var_o(obj, "T", "<=", 0)],
          [poner_estado(obj, siguiente), var_o(obj, "T", "=", t_siguiente), *acciones]),
    ]


def eventos_enemigos():
    R, AC, CU, AG = "Repintado", "Actor", "Cuervo", "Agente"
    EN, PR, ON = "Enemigo", "ProyectilEnemigo", "Onda"
    golpeable = [si_var_o(V, "Invulnerable", "<=", 0), si_var_o(V, "Muerto", "=", 0),
                 si_var_o(V, "ParryVentana", "<=", 0)]
    return [
        GRUPO("Repintado: patrulla y ataque telegrafiado", [
            NOTA("Cada enemigo cuida su propio tramo: su rango de patrulla se calcula desde SU "
                 "posición inicial (variable Rango por instancia). Ninguno cruza el nivel."),
            *patrulla(R),
            NOTA("Patrón de tres tiempos: aviso (levanta las garras 0,5 s), embestida corta y "
                 "recuperación lenta. El aviso le da tiempo al jugador para saltar o hacer "
                 "parry, y la recuperación es la ventana de castigo."),
            E([estado_es(R, "patrulla"), *en_rango(R, 70, 30)],
              [poner_estado(R, "preparar"), var_o(R, "T", "=", 0.5),
               var_o(R, "Dir", "=", f"sign({V}.X() - {R}.X())"), anim(R, "Preparar"),
               sonido_fx("repintado_aviso", 45)]),
            E([estado_es(R, "preparar")], [var_o(R, "T", "-", DT)]),
            PARA_CADA(R, [estado_es(R, "preparar"), si_var_o(R, "T", "<=", 0)],
                      [poner_estado(R, "atacar"), var_o(R, "T", "=", 0.35), anim(R, "Atacar"),
                       crear("Zarpazo", f"{R}.X() + {R}.Variable(Dir) * 20", f"{R}.Y() - 28")]),
            E([estado_es(R, "atacar")],
              [var_o(R, "T", "-", DT), A("SetX", R, "+", f"{R}.Variable(Dir) * 130 * {DT}")]),
            E([estado_es(R, "atacar"), si_var_o(R, "T", "<=", 0)],
              [poner_estado(R, "recuperar"), var_o(R, "T", "=", 0.8), anim(R, "Idle")]),
            *cuenta_regresiva(R, "recuperar", "patrulla", 0),
            NOTA("Parry contra la embestida: el Repintado queda aturdido 1,2 s. Así el nivel 1 "
                 "enseña el parry contra un ataque cuerpo a cuerpo antes de los proyectiles."),
            E([si_var_o(V, "ParryVentana", ">", 0), choca(V, R), estado_es(R, "atacar")],
              [poner_estado(R, "aturdido"), var_o(R, "T", "=", 1.2), anim(R, "Golpeado"),
               *efecto_parry(),
               var_o(V, "Mana", "+", 15), var_s("Hitstop", "=", 6), var_s("Temblor", "=", 3),
               var_s("Parries", "+", 1), sonido_fx("parry")]),
            *cuenta_regresiva(R, "aturdido", "patrulla", 0),
            E([anim_termino("Zarpazo")], [borrar("Zarpazo")]),
        ], color="enemigo"),
        GRUPO("Actor: ataque a distancia", [
            NOTA("El Actor no se acerca: se planta a distancia media y tira una máscara recta, "
                 "a la altura del pecho. Se esquiva saltando o se devuelve con parry; la pausa "
                 "larga después de tirar es el momento de acercarse."),
            *patrulla(AC),
            E([estado_es(AC, "patrulla"), *en_rango(AC, 210, 50, 60)],
              [poner_estado(AC, "preparar"), var_o(AC, "T", "=", 0.6),
               var_o(AC, "Dir", "=", f"sign({V}.X() - {AC}.X())"), anim(AC, "Preparar"),
               sonido_fx("actor_aviso", 45)]),
            E([estado_es(AC, "preparar")], [var_o(AC, "T", "-", DT)]),
            PARA_CADA(AC, [estado_es(AC, "preparar"), si_var_o(AC, "T", "<=", 0)],
                      [poner_estado(AC, "lanzar"), var_o(AC, "T", "=", 0.3), anim(AC, "Lanzar"),
                       crear("Mascara", f"{AC}.X() + {AC}.Variable(Dir) * 16", f"{AC}.Y() - 30"),
                       var_o("Mascara", "Dir", "=", f"{AC}.Variable(Dir)"),
                       sonido_fx("mascara", 50)]),
            *cuenta_regresiva(AC, "lanzar", "recuperar", 1.4, [anim(AC, "Recuperar")]),
            *cuenta_regresiva(AC, "recuperar", "patrulla", 0),
        ], color="enemigo"),
        GRUPO("Cuervo: vuelo y picada", [
            NOTA("Vuela en su zona con un vaivén vertical. Si Ventura pasa por debajo, se queda "
                 "quieto un instante (aviso) y se tira en picada hacia donde ESTABA: la dirección "
                 "se fija al empezar, así moverse a tiempo siempre lo esquiva."),
            E([si_var_o(CU, "Iniciado", "=", 0)],
              [var_o(CU, "Izq", "=", f"{CU}.X() - {CU}.Variable(Rango)"),
               var_o(CU, "Der", "=", f"{CU}.X() + {CU}.Variable(Rango)"),
               var_o(CU, "X0", "=", f"{CU}.X()"), var_o(CU, "Y0", "=", f"{CU}.Y()"),
               var_o(CU, "Iniciado", "=", 1)]),
            E([estado_es(CU, "volar")],
              [A("SetX", CU, "+", f"{CU}.Variable(Dir) * {CU}.Variable(Vel) * {DT}"),
               A("SetY", CU, "=", f"{CU}.Variable(Y0) + sin(Variable(Tiempo) * 3 + {CU}.Variable(X0) * 0.05) * 6"),
               anim(CU, "Volar")]),
            E([estado_es(CU, "volar"), C("PosX", CU, "<", f"{CU}.Variable(Izq)")], [var_o(CU, "Dir", "=", 1)]),
            E([estado_es(CU, "volar"), C("PosX", CU, ">", f"{CU}.Variable(Der)")], [var_o(CU, "Dir", "=", -1)]),
            E([estado_es(CU, "volar"), C("PosX", CU, ">", f"{V}.X() - 120"),
               C("PosX", CU, "<", f"{V}.X() + 120"), C("PosY", CU, "<", f"{V}.Y() - 40"),
               C("PosY", CU, ">", f"{V}.Y() - 230"), si_var_o(V, "Muerto", "=", 0)],
              [poner_estado(CU, "preparar"), var_o(CU, "T", "=", 0.4),
               var_o(CU, "Dir", "=", f"sign({V}.X() - {CU}.X())"), sonido_fx("cuervo", 45)]),
            E([estado_es(CU, "preparar")],
              [var_o(CU, "T", "-", DT),
               A("SetY", CU, "-", f"20 * {DT}")]),
            E([estado_es(CU, "preparar"), si_var_o(CU, "T", "<=", 0)],
              [poner_estado(CU, "picada"), var_o(CU, "T", "=", 0), anim(CU, "Picada"),
               var_o(CU, "VX", "=", f"cos(atan2({V}.Y() - 22 - {CU}.Y(), {V}.X() - {CU}.X())) * 240"),
               var_o(CU, "VY", "=", f"sin(atan2({V}.Y() - 22 - {CU}.Y(), {V}.X() - {CU}.X())) * 240")]),
            E([estado_es(CU, "picada")],
              [var_o(CU, "T", "+", DT),
               A("SetX", CU, "+", f"{CU}.Variable(VX) * {DT}"),
               A("SetY", CU, "+", f"{CU}.Variable(VY) * {DT}")]),
            E([estado_es(CU, "picada"), O(choca(CU, "Suelo"), si_var_o(CU, "T", ">", 1.1))],
              [poner_estado(CU, "subir"), anim(CU, "Volar")]),
            E([estado_es(CU, "subir")], [A("SetY", CU, "-", f"90 * {DT}")]),
            E([estado_es(CU, "subir"), C("PosY", CU, "<=", f"{CU}.Variable(Y0)")],
              [poner_estado(CU, "volar")]),
        ], color="enemigo"),
        GRUPO("Agente: golpe al piso y casco", [
            NOTA("El enemigo pesado: camina lento, avisa con el garrote en alto 0,75 s y golpea "
                 "el piso soltando dos ondas que corren en direcciones opuestas. Es el que obliga "
                 "a saltar en el momento justo, no a alejarse."),
            *patrulla(AG),
            E([estado_es(AG, "patrulla"), *en_rango(AG, 120, 40)],
              [poner_estado(AG, "preparar"), var_o(AG, "T", "=", 0.75),
               var_o(AG, "Dir", "=", f"sign({V}.X() - {AG}.X())"), anim(AG, "Preparar"),
               sonido_fx("agente_aviso", 50)]),
            E([estado_es(AG, "preparar")], [var_o(AG, "T", "-", DT)]),
            PARA_CADA(AG, [estado_es(AG, "preparar"), si_var_o(AG, "T", "<=", 0)],
                      [poner_estado(AG, "golpe"), var_o(AG, "T", "=", 0.35), anim(AG, "Golpe"),
                       crear("OndaSuelo", f"{AG}.X() + 18", f"{AG}.Y()"),
                       var_o("OndaSuelo", "Dir", "=", 1),
                       crear("OndaSuelo", f"{AG}.X() - 18", f"{AG}.Y()"),
                       var_o("OndaSuelo", "Dir", "=", -1),
                       var_s("Temblor", "=", 3), sonido_fx("golpe_suelo", 60)]),
            *cuenta_regresiva(AG, "golpe", "recuperar", 1.1, [anim(AG, "Idle")]),
            *cuenta_regresiva(AG, "recuperar", "patrulla", 0),
            NOTA("El casco: una carta sin cargar rebota. Es la regla que enseña a usar la carga "
                 "(o el farol) contra los enemigos fuertes; el primer rebote lo explica en "
                 "pantalla."),
            E([choca("Carta", AG), si_var_o("Carta", "Nivel", "=", 1), estado_es(AG, "muerto", neg=True)],
              [crear("Chispa", "Carta.X()", "Carta.Y()"), borrar("Carta"), sonido_fx("bloqueo", 50)],
              [E([si_var_s("AvisoCasco", "=", 0)],
                 [var_s("AvisoCasco", "=", 1), var_s("AvisoT", "=", 3),
                  texto("TextoAviso", '"El casco frena las cartas débiles: cargá antes de tirar"')])]),
        ], color="enemigo"),
        GRUPO("Ondas y proyectiles enemigos", [
            NOTA("Ondas (del Agente y del Aullido del jefe): corren a ras del piso y se saltan."),
            E([], [A("SetX", ON, "+", f"{ON}.Variable(Dir) * {ON}.Variable(Vel) * {DT}"),
                   var_o(ON, "T", "+", DT)]),
            E([si_var_o(ON, "T", ">", f"{ON}.Variable(Duracion)")], [borrar(ON)]),
            E([*golpeable[:2], choca(V, ON)],
              [var_o(V, "Dano", "=", f"{ON}.Variable(Dano)"),
               var_o(V, "EmpujeDir", "=", f"{ON}.Variable(Dir)")]),
            NOTA("Proyectiles: el parry los devuelve más rápido y del lado del jugador. El parry "
                 "va ANTES que el daño a propósito: si la ventana está abierta, nunca llega a "
                 "lastimar."),
            E([], [A("SetX", PR, "+", f"{PR}.Variable(Dir) * {PR}.Variable(Vel) * {DT}"),
                   var_o(PR, "T", "+", DT)]),
            E([si_var_o("Mascara", "Dir", "=", -1)], [voltear("Mascara", True)]),
            E([si_var_o("Mascara", "Dir", "=", 1)], [voltear("Mascara", False)]),
            E([si_var_o("GarraLuna", "Dir", "=", 1)], [voltear("GarraLuna", True)]),
            E([si_var_o("GarraLuna", "Dir", "=", -1)], [voltear("GarraLuna", False)]),
            E([si_var_o(V, "ParryVentana", ">", 0), choca(V, PR), si_var_o(PR, "Reflejada", "=", 0)],
              [var_o(PR, "Reflejada", "=", 1), var_o(PR, "Dir", "=", f"-{PR}.Variable(Dir)"),
               var_o(PR, "Vel", "*", 1.8), var_o(PR, "T", "=", 0),
               *efecto_parry(),
               var_o(V, "Mana", "+", 15), var_s("Hitstop", "=", 6), var_s("Temblor", "=", 3),
               var_s("Parries", "+", 1), sonido_fx("parry")]),
            E([*golpeable, choca(V, PR), si_var_o(PR, "Reflejada", "=", 0)],
              [var_o(V, "Dano", "=", f"{PR}.Variable(Dano)"),
               var_o(V, "EmpujeDir", "=", f"{PR}.Variable(Dir)"),
               crear("Chispa", f"{PR}.X()", f"{PR}.Y()"), borrar(PR)]),
            E([si_var_o(PR, "Reflejada", "=", 1), choca(PR, EN), estado_es(EN, "muerto", neg=True)],
              [var_o(EN, "Vida", "-", 30), var_o(EN, "Golpe", "=", 0.2),
               crear("Impacto", f"{PR}.X()", f"{PR}.Y()"), var_s("Hitstop", "=", 3),
               borrar(PR), sonido_fx("golpe")]),
            E([O(choca(PR, "Suelo"), si_var_o(PR, "T", ">", 3.5))],
              [crear("Chispa", f"{PR}.X()", f"{PR}.Y()"), borrar(PR)]),
        ], color="enemigo"),
        GRUPO("Enemigos: golpes, contacto y muerte (comunes)", [
            NOTA("Todo lo que comparten los cuatro enemigos se resuelve una sola vez sobre el "
                 "grupo Enemigo. Las máquinas de estado de arriba sólo deciden QUÉ hace cada uno."),
            E([si_var_o(EN, "Dir", "=", 1)], [voltear(EN, False)]),
            E([si_var_o(EN, "Dir", "=", -1)], [voltear(EN, True)]),
            E([*golpeable, choca(V, EN), estado_es(EN, "muerto", neg=True)],
              [var_o(V, "Dano", "=", f"{EN}.Variable(Contacto)"),
               var_o(V, "EmpujeDir", "=", f"sign({V}.X() - {EN}.X())")],
              [E([estado_es(R, "atacar"), choca(V, R)], [var_o(V, "Dano", "=", 15)]),
               E([estado_es(CU, "picada"), choca(V, CU)], [var_o(V, "Dano", "=", 14)])]),
            E([choca("Carta", EN), estado_es(EN, "muerto", neg=True), si_var_o("Carta", "Nivel", "=", 3)],
              [crear("Explosion", "Carta.X()", "Carta.Y()"), var_s("Temblor", "=", 5),
               sonido_fx("explosion", 65)]),
            E([choca("Carta", EN), estado_es(EN, "muerto", neg=True)],
              [var_o(EN, "Vida", "-", "Carta.Variable(Dano)"), var_o(EN, "Golpe", "=", 0.15),
               crear("Impacto", "Carta.X()", "Carta.Y()"), var_s("Hitstop", "=", 2),
               borrar("Carta"), sonido_fx("golpe")]),
            E([C("CollisionNP", "Explosion", EN, "", "", ""), si_var_o("Explosion", "Activa", "=", 1),
               estado_es(EN, "muerto", neg=True)],
              [var_o(EN, "Vida", "-", 35), var_o(EN, "Golpe", "=", 0.2)]),
            E([si_var_o(EN, "Golpe", ">", 0)],
              [var_o(EN, "Golpe", "-", DT), A("ChangeColor", EN, '"190;150;255"')]),
            E([si_var_o(EN, "Golpe", "<=", 0)], [A("ChangeColor", EN, '"255;255;255"')]),
            NOTA("La animación de golpe sólo pisa a las de estados tranquilos: si el enemigo está "
                 "avisando o atacando, el aviso tiene que seguir leyéndose."),
            E([si_var_o(EN, "Golpe", ">", 0),
               O(estado_es(EN, "patrulla"), estado_es(EN, "recuperar"), estado_es(EN, "volar"),
                 estado_es(EN, "subir"))], [anim(EN, "Golpeado")]),
            NOTA("Al morir, la tinta del enemigo se derrite (animación Morir) y recién al terminar "
                 "se lo saca: el vecino queda libre. Puede dejar té (vida) o luna (maná)."),
            E([si_var_o(EN, "Vida", "<=", 0), estado_es(EN, "muerto", neg=True)],
              [poner_estado(EN, "muerto"), anim(EN, "Morir"), var_s("Temblor", "=", 2),
               var_s("Vencidos", "+", 1), sonido_fx("tinta")]),
            PARA_CADA(EN, [estado_es(EN, "muerto"), anim_termino(EN)],
                      [crear("Tinta", f"{EN}.X()", f"{EN}.Y()")],
                      [E([comparar("Random(9)", "<", 3)], [crear("Te", f"{EN}.X()", f"{EN}.Y()")]),
                       E([comparar("Random(9)", ">=", 6)], [crear("Luna", f"{EN}.X()", f"{EN}.Y() - 8")]),
                       E([], [borrar(EN)])]),
            E([anim_termino("Tinta")], [borrar("Tinta")]),
        ], color="enemigo"),
    ]


def si_texto_o(obj, var, op, valor):
    return C("StringObjectVariable", obj, var, op, valor)


# =================================================================== EVENTOS: OBSTÁCULOS

def eventos_obstaculos():
    return [
        GRUPO("Plataformas móviles y nubes de tinta", [
            NOTA("Movimiento armónico (seno) desde la posición inicial: se frena en los "
                 "extremos, así el jugador puede leer cuándo subirse. El comportamiento de "
                 "plataformas arrastra a Ventura con la plataforma."),
            E([si_var_o("Andamio", "Iniciado", "=", 0)],
              [var_o("Andamio", "X0", "=", "Andamio.X()"), var_o("Andamio", "Y0", "=", "Andamio.Y()"),
               var_o("Andamio", "Iniciado", "=", 1)]),
            E([], [A("SetXY", "Andamio", "=",
                     "Andamio.Variable(X0) + sin(Variable(Tiempo) * Andamio.Variable(Vel) + Andamio.Variable(Fase)) * Andamio.Variable(DX)",
                     "=",
                     "Andamio.Variable(Y0) + sin(Variable(Tiempo) * Andamio.Variable(Vel) + Andamio.Variable(Fase)) * Andamio.Variable(DY)")]),
            E([si_var_o("NubeTinta", "Iniciado", "=", 0)],
              [var_o("NubeTinta", "X0", "=", "NubeTinta.X()"),
               var_o("NubeTinta", "Y0", "=", "NubeTinta.Y()"),
               var_o("NubeTinta", "Iniciado", "=", 1)]),
            E([], [A("SetXY", "NubeTinta", "=",
                     "NubeTinta.Variable(X0) + sin(Variable(Tiempo) * NubeTinta.Variable(Vel) + NubeTinta.Variable(Fase)) * NubeTinta.Variable(DX)",
                     "=",
                     "NubeTinta.Variable(Y0) + sin(Variable(Tiempo) * NubeTinta.Variable(Vel) + NubeTinta.Variable(Fase)) * NubeTinta.Variable(DY)")]),
        ], color="nivel"),
        GRUPO("Péndulos", [
            NOTA("Bolsas de arena de la tramoya (y péndulos de reloj en el nivel 3): el ángulo "
                 "sigue un seno, igual que las plataformas, así se frenan en los extremos y el "
                 "jugador puede medir cuándo pasar por abajo. La fase por instancia desfasa "
                 "péndulos vecinos para que no se muevan todos juntos."),
            E([], [A("SetAngle", "Pendulo", "=",
                     "sin(Variable(Tiempo) * Pendulo.Variable(Vel) + Pendulo.Variable(Fase)) * Pendulo.Variable(Amplitud)")]),
        ], color="nivel"),
        GRUPO("Tablones podridos", [
            NOTA("Tres estados: sano → cruje (0,45 s de aviso, el tablón tiembla) → cae. "
                 "Vuelve a su lugar a los 3 s para que el camino nunca quede cerrado."),
            E([si_var_o("Tablon", "Iniciado", "=", 0)],
              [var_o("Tablon", "X0", "=", "Tablon.X()"), var_o("Tablon", "Y0", "=", "Tablon.Y()"),
               var_o("Tablon", "Iniciado", "=", 1)]),
            E([C("PlatformBehavior::IsObjectOnGivenFloor", V, "PlatformerObject", "Tablon", ""),
               si_var_o("Tablon", "Estado", "=", 0)],
              [var_o("Tablon", "Estado", "=", 1), var_o("Tablon", "T", "=", 0.45),
               anim("Tablon", "Cruje"), sonido_fx("cruje", 50)]),
            E([si_var_o("Tablon", "Estado", "=", 1)],
              [var_o("Tablon", "T", "-", DT),
               A("SetX", "Tablon", "=", "Tablon.Variable(X0) + RandomInRange(-1, 1)")]),
            E([si_var_o("Tablon", "Estado", "=", 1), si_var_o("Tablon", "T", "<=", 0)],
              [var_o("Tablon", "Estado", "=", 2), var_o("Tablon", "T", "=", 3),
               var_o("Tablon", "VelY", "=", 0), anim("Tablon", "Roto"),
               A("SetX", "Tablon", "=", "Tablon.Variable(X0)"),
               A("ActivateBehavior", "Tablon", "Platform", "no")]),
            E([si_var_o("Tablon", "Estado", "=", 2)],
              [var_o("Tablon", "T", "-", DT), var_o("Tablon", "VelY", "+", f"600 * {DT}"),
               A("SetY", "Tablon", "+", f"Tablon.Variable(VelY) * {DT}")]),
            E([si_var_o("Tablon", "Estado", "=", 2), si_var_o("Tablon", "T", "<=", 0)],
              [var_o("Tablon", "Estado", "=", 0), anim("Tablon", "Sano"),
               A("SetXY", "Tablon", "=", "Tablon.Variable(X0)", "=", "Tablon.Variable(Y0)"),
               A("ActivateBehavior", "Tablon", "Platform", "yes")]),
        ], color="nivel"),
        GRUPO("Toldos elásticos", [
            NOTA("Rebote de dibujo animado: sólo si Ventura CAE sobre el toldo desde arriba. "
                 "El rebote usa una velocidad de salto mayor (760, unos 120 px) y devuelve el doble salto; "
                 "al tocar el piso la velocidad de salto vuelve a la normal."),
            NOTA("Cayendo rápido Ventura baja hasta 16 px por cuadro: si se exigiera que los pies "
                 "estén por encima del toldo, el rebote se perdería entre un cuadro y otro. Por "
                 "eso alcanza con que no hayan pasado la base del toldo, o con que justo esté "
                 "aterrizando (acción Aterrizaje recién iniciada)."),
            E([choca(V, "Toldo"), C("PosY", V, "<=", "Toldo.Y() + 1"),
               O(C("PlatformBehavior::IsFalling", V, "PlatformerObject"),
                 C("StringObjectVariable", V, "Accion", "=", '"Aterrizaje"'))],
              [A("PlatformBehavior::PlatformerObjectBehavior::SetCurrentFallSpeed", V, "PlatformerObject", "=", 0),
               A("PlatformBehavior::JumpSpeed", V, "PlatformerObject", "=", 760),
               A("PlatformBehavior::SetCanJump", V, "PlatformerObject"),
               A("PlatformBehavior::SimulateJumpKey", V, "PlatformerObject"),
               var_o(V, "SaltoAereo", "=", 0), anim("Toldo", "Aplastado"),
               var_o("Toldo", "T", "=", 0.25), sonido_fx("rebote")]),
            E([si_var_o("Toldo", "T", ">", 0)], [var_o("Toldo", "T", "-", DT)]),
            E([si_var_o("Toldo", "T", ">", 0), si_var_o("Toldo", "T", "<", 0.15)],
              [anim("Toldo", "Estirado")]),
            E([si_var_o("Toldo", "T", "<=", 0)], [anim("Toldo", "Reposo")]),
        ], color="nivel"),
        GRUPO("Engranajes que caen", [
            NOTA("Cada 'Caedor' (invisible) suelta un engranaje cada Periodo segundos. Se usa "
                 "'para cada' porque la creación necesita la posición de ESE caedor."),
            E([], [var_o("Caedor", "T", "+", DT)]),
            PARA_CADA("Caedor", [si_var_o("Caedor", "T", ">=", "Caedor.Variable(Periodo)")],
                      [var_o("Caedor", "T", "=", 0),
                       crear("Engranaje", "Caedor.X()", "Caedor.Y()")]),
            E([], [var_o("Engranaje", "VelY", "=", f"min(380, Engranaje.Variable(VelY) + 600 * {DT})"),
                   A("SetY", "Engranaje", "+", f"Engranaje.Variable(VelY) * {DT}")]),
            E([choca("Engranaje", "Suelo")],
              [crear("Polvo", "Engranaje.X()", "Engranaje.Y() + 10"), borrar("Engranaje"),
               sonido_fx("engranaje", 30)]),
            E([C("PosY", "Engranaje", ">", "Variable(NivelAlto) + 40")], [borrar("Engranaje")]),
        ], color="nivel"),
        GRUPO("Barriles", [
            E([O(choca("Carta", "Barril"), C("CollisionNP", "Explosion", "Barril", "", "", "")),
               si_var_o("Barril", "Roto", "=", 0)],
              [var_o("Barril", "Roto", "=", 1), anim("Barril", "Roto"),
               A("ActivateBehavior", "Barril", "Platform", "no"), sonido_fx("barril")],
              [PARA_CADA("Barril", [si_var_o("Barril", "Roto", "=", 1),
                                    anim_es("Barril", "Roto")],
                         [], [E([comparar("Random(1)", "=", 0)],
                                [crear("Te", "Barril.X()", "Barril.Y()")]),
                              E([comparar("Random(1)", "=", 1)],
                                [crear("Luna", "Barril.X()", "Barril.Y() - 8")])])]),
            E([choca("Carta", "Barril")], [borrar("Carta")]),
            E([si_var_o("Barril", "Roto", "=", 1), anim_termino("Barril")], [borrar("Barril")]),
        ], color="nivel"),
        GRUPO("Objetos para recoger", [
            E([choca(V, "Te")],
              [var_o(V, "Vida", "=", f"min({VAR('VidaMax')}, {VAR('Vida')} + 30)"),
               crear("Destello", "Te.X()", "Te.Y() - 8"), borrar("Te"), sonido_fx("te")]),
            E([choca(V, "Luna")],
              [var_o(V, "Mana", "=", f"min({VAR('ManaMax')}, {VAR('Mana')} + 40)"),
               crear("Destello", "Luna.X()", "Luna.Y() - 6"), borrar("Luna"), sonido_fx("luna")]),
            E([anim_termino("Destello")], [borrar("Destello")]),
            E([anim_termino("Polvo")], [borrar("Polvo")]),
            E([anim_termino("Impacto")], [borrar("Impacto")]),
            E([anim_termino("Chispa")], [borrar("Chispa")]),
            E([anim_termino("ParryFx")], [borrar("ParryFx")]),
        ], color="nivel"),
    ]


# =================================================================== EVENTOS: CÁMARA

def eventos_camara():
    clamp_x = "clamp(Variable(CamX), 320, Variable(NivelAncho) - 320)"
    clamp_y = "clamp(Variable(CamY), 180, Variable(NivelAlto) - 180)"
    return [
        GRUPO("Seguimiento suave", [
            NOTA("La cámara no se pega al personaje: persigue un punto adelantado hacia donde "
                 "mira (36 px), para mostrar más de lo que viene, y lo hace con suavizado "
                 "exponencial. Los límites se aplican a mano (clamp) en vez de usar "
                 "ClampCamera, para poder sumar el temblor después del límite."),
            E([al_iniciar()],
              [var_s("CamX", "=", f"{V}.X()"), var_s("CamY", "=", f"{V}.Y() - 40"),
               var_s("MiraCam", "=", VAR("Mirando"))]),
            NOTA("El adelanto no salta de un lado al otro al darse vuelta: MiraCam sigue a "
                 "Mirando con su propio suavizado, más lento que el de la cámara, así un cambio "
                 "de dirección corto no sacude la pantalla."),
            E([], [var_s("MiraCam", "+", f"({VAR('Mirando')} - Variable(MiraCam)) * min(1, 2.5 * {DT})")]),
            E([], [var_s("CamX", "+", f"({V}.X() + Variable(MiraCam) * 36 - Variable(CamX)) * min(1, 5 * {DT})"),
                   var_s("CamY", "+", f"({V}.Y() - 40 - Variable(CamY)) * min(1, 4 * {DT})"),
                   var_s("CamX", "=", clamp_x), var_s("CamY", "=", clamp_y)]),
            E([si_var_s("Temblor", ">", 0)],
              [var_s("Temblor", "=", f"max(0, Variable(Temblor) - 24 * {DT})")]),
            E([], [A("SetCameraCenterX", "", "=",
                     "Variable(CamX) + RandomFloatInRange(-Variable(Temblor), Variable(Temblor))",
                     '""', 0),
                   A("SetCameraCenterY", "", "=",
                     "Variable(CamY) + RandomFloatInRange(-Variable(Temblor), Variable(Temblor))",
                     '""', 0)]),
        ], color="camara"),
        GRUPO("Parallax", [
            NOTA("Cada capa de fondo se mueve una fracción del recorrido de la cámara. El "
                 "factor de la ciudad se calcula para que la tira ilustrada del barrio cubra "
                 "exactamente el nivel: (anchoFondo - 640) / (anchoNivel - 640)."),
            E([], [A("SetCameraCenterX", "", "=", "320 + (Variable(CamX) - 320) * Variable(FactorCieloX)", '"Cielo"', 0),
                   A("SetCameraCenterY", "", "=", "180 + (Variable(CamY) - 180) * Variable(FactorCieloY)", '"Cielo"', 0),
                   A("SetCameraCenterX", "", "=", "320 + (Variable(CamX) - 320) * Variable(FactorCiudadX)", '"Ciudad"', 0),
                   A("SetCameraCenterY", "", "=", "180 + (Variable(CamY) - 180) * Variable(FactorCiudadY)", '"Ciudad"', 0)]),
            NOTA("Nubes y bruma son mosaicos en capas fijas: se desplaza la textura (offset) "
                 "con la cámara y con el viento, así nunca se terminan."),
            E([], [var_s("Tiempo", "+", DT),
                   A("TiledSpriteObject::XOffset", "NubesLejos", "=", "(Variable(CamX) - 320) * 0.08 + Variable(Tiempo) * 4"),
                   A("TiledSpriteObject::XOffset", "NubesCerca", "=", "(Variable(CamX) - 320) * 0.16 + Variable(Tiempo) * 9"),
                   A("TiledSpriteObject::XOffset", "Bruma", "=", "(Variable(CamX) - 320) * 1.3 + Variable(Tiempo) * 14")]),
        ], color="camara"),
    ]


# =================================================================== EVENTOS: HUD

def eventos_hud():
    return [
        GRUPO("Vida y maná", [
            NOTA("Cinco cartas de vida de 20 puntos cada una (media carta = 10). Se recorre "
                 "cada carta con 'para cada' porque cada una compara contra su propio Indice."),
            PARA_CADA("CartaVida", [], [anim("CartaVida", "Vacia")], [
                E([comparar(VAR("Vida"), ">=", "CartaVida.Variable(Indice) * 20 + 10")],
                  [anim("CartaVida", "Media")]),
                E([comparar(VAR("Vida"), ">=", "CartaVida.Variable(Indice) * 20 + 20")],
                  [anim("CartaVida", "Llena")])]),
            E([], [ancho("BarraMana", "=", f"58 * {VAR('Mana')} / {VAR('ManaMax')}")]),
        ], color="hud"),
        GRUPO("Medidor de carga", [
            NOTA("El medidor flota sobre la cabeza sólo mientras se carga: la información "
                 "aparece donde el jugador está mirando, no en una esquina."),
            E([si_var_o(V, "Cargando", "=", 1)],
              [A("Show", "BarraCargaFondo", ""), A("Show", "BarraCarga", ""),
               A("SetXY", "BarraCargaFondo", "=", f"{V}.X()", "=", f"{V}.Y() - 56"),
               A("SetXY", "BarraCarga", "=", f"{V}.X() - 11", "=", f"{V}.Y() - 56"),
               ancho("BarraCarga", "=", f"max(1, 22 * {VAR('Carga')} / 100)"),
               A("AnimatableCapability::AnimatableBehavior::SetName", "BarraCarga", "Animation",
                 "=", f'"Nivel" + ToString(min(3, 1 + floor({VAR("Carga")} / 45)))')]),
            E([si_var_o(V, "Cargando", "=", 0)],
              [A("Hide", "BarraCargaFondo"), A("Hide", "BarraCarga")]),
        ], color="hud"),
        GRUPO("Avisos", [
            NOTA("Los avisos llevan un recuadro oscuro detrás, del ancho del texto: sobre los "
                 "fondos ilustrados, la letra clara sola se perdía (devolución del Game Test)."),
            E([], [A("SetX", "TextoAviso", "=", "320 - TextoAviso.Width() / 2"),
                   A("SetX", "TextoPausa", "=", "320 - TextoPausa.Width() / 2"),
                   A("SetX", "FondoAviso", "=", "320 - TextoAviso.Width() / 2 - 8"),
                   ancho("FondoAviso", "=", "TextoAviso.Width() + 16")]),
            E([si_var_s("AvisoT", ">", 0)],
              [var_s("AvisoT", "-", DT), A("Show", "TextoAviso", ""), A("Show", "FondoAviso", ""),
               opacidad("TextoAviso", "=", "min(255, Variable(AvisoT) * 400)"),
               opacidad("FondoAviso", "=", "min(220, Variable(AvisoT) * 350)")]),
            E([si_var_s("AvisoT", "<=", 0)], [A("Hide", "TextoAviso"), A("Hide", "FondoAviso")]),
        ], color="hud"),
        GRUPO("Cartel de golpe y fogonazo", [
            NOTA("El cartel (¡PARRY!) sube y se desvanece en algo más de medio segundo. El "
                 "fogonazo blanco tapa la pantalla un instante y se apaga solo: Flash baja a "
                 "velocidad fija, así cualquier evento sólo tiene que ponerlo en un valor."),
            E([], [A("SetY", "TextoGolpe", "-", f"40 * {DT}"),
                   opacidad("TextoGolpe", "-", f"380 * {DT}")]),
            E([C("OpacityCapability::OpacityBehavior::Value", "TextoGolpe", "Opacity", "<=", 0)],
              [borrar("TextoGolpe")]),
            E([], [var_s("Flash", "=", f"max(0, Variable(Flash) - 3 * {DT})"),
                   opacidad("Blanco", "=", "Variable(Flash) * 255")]),
        ], color="hud"),
        GRUPO("Fin del cuadro", [
            NOTA("La explosión del farol lastima sólo en el cuadro en que aparece: este evento va "
                 "último (la hoja HUD se enlaza al final) para que todas las hojas de daño la "
                 "vean activa una vez y después ya no."),
            E([], [var_o("Explosion", "Activa", "=", 0)]),
        ], color="hud"),
    ]


# =================================================================== EVENTOS: DIÁLOGO

def eventos_dialogo():
    linea = "VariableString(Dialogo.Linea)"
    sep = f'StrFind({linea}, "|")'
    cuerpo = f"SubStr({linea}, {sep} + 1, StrLength({linea}))"
    actual = "VariableString(Guion[VariableString(Dialogo.Set)][Variable(Dialogo.Indice)])"
    total = "VariableChildCount(Guion[VariableString(Dialogo.Set)])"
    avanzar = O(tecla_recien("Return"), tecla_recien("Space"), tecla_recien("x"), tecla_recien("z"),
                C("HasAnyTouchStarted", ""))
    return [
        GRUPO("Disparadores", [
            NOTA("Los diálogos de cada escena viven en la variable de escena Guion (un arreglo "
                 "de líneas 'Nombre|Texto' por cada Id). Una ZonaDialogo invisible con ese Id "
                 "lo dispara una sola vez."),
            E([choca(V, "ZonaDialogo"), si_var_o("ZonaDialogo", "Visto", "=", 0),
               si_var_s("Dialogo.Activo", "=", 0), si_var_o(V, "Muerto", "=", 0)],
              [var_o("ZonaDialogo", "Visto", "=", 1),
               texto_s("Dialogo.Set", "ZonaDialogo.VariableString(Id)"),
               texto_s("Dialogo.Despues", "ZonaDialogo.VariableString(Despues)"),
               var_s("Dialogo.Activo", "=", 1), var_s("Dialogo.Indice", "=", 0),
               var_s("Dialogo.Chars", "=", 0), var_s("Bloqueado", "=", 1),
               var_o(V, "Cargando", "=", 0), A("ShowLayer", "", '"Dialogo"')]),
        ]),
        GRUPO("Caja de texto", [
            NOTA("Efecto máquina de escribir: se muestran floor(Chars) letras y Chars crece "
                 "45 por segundo. Apretar mientras escribe completa la línea; apretar con la "
                 "línea completa pasa a la siguiente."),
            E([si_var_s("Dialogo.Activo", "=", 1)],
              [texto_s("Dialogo.Linea", actual),
               var_s("Dialogo.Chars", "+", f"45 * {DT}"),
               texto("NombreDialogo", f"SubStr({linea}, 0, {sep})"),
               texto("TextoDialogo", f"SubStr({cuerpo}, 0, floor(Variable(Dialogo.Chars)))"),
               A("AnimatableCapability::AnimatableBehavior::SetName", "RetratoDialogo", "Animation",
                 "=", f"SubStr({linea}, 0, {sep})")]),
            NOTA("El retrato es la animación con el nombre de quien habla. Ambrosio tiene dos: "
                 "en la torre, mientras es lobo, la variable RetratoAmbrosio vale \"Lobo\"."),
            E([si_var_s("Dialogo.Activo", "=", 1),
               comparar_texto(f"SubStr({linea}, 0, {sep})", "=", '"Ambrosio"')],
              [A("AnimatableCapability::AnimatableBehavior::SetName", "RetratoDialogo", "Animation",
                 "=", "VariableString(RetratoAmbrosio)")]),
            E([si_var_s("Dialogo.Activo", "=", 1), avanzar,
               comparar("Variable(Dialogo.Chars)", ">=", f"StrLength({cuerpo})")],
              [var_s("Dialogo.Indice", "+", 1), var_s("Dialogo.Chars", "=", 0),
               var_s("Dialogo.Avanzo", "=", 1), sonido_fx("dialogo", 30)]),
            E([si_var_s("Dialogo.Activo", "=", 1), si_var_s("Dialogo.Avanzo", "=", 0), avanzar],
              [var_s("Dialogo.Chars", "=", 999)]),
            E([], [var_s("Dialogo.Avanzo", "=", 0)]),
            E([si_var_s("Dialogo.Activo", "=", 1),
               comparar("Variable(Dialogo.Chars)", ">=", f"StrLength({cuerpo})")],
              [A("Show", "Seguir", "")]),
            E([comparar("Variable(Dialogo.Chars)", "<", f"StrLength({cuerpo})")],
              [A("Hide", "Seguir")]),
            E([si_var_s("Dialogo.Activo", "=", 1),
               comparar("Variable(Dialogo.Indice)", ">=", total)],
              [var_s("Dialogo.Activo", "=", 0), var_s("Bloqueado", "=", 0),
               A("HideLayer", "", '"Dialogo"')],
              [E([si_texto_s("Dialogo.Despues", "=", '"salir"')],
                 [var_s("Saliendo", "=", 1), var_s("Bloqueado", "=", 1),
                  var_s("FundidoObjetivo", "=", 1)])]),
        ]),
    ]


# =================================================================== EVENTOS: NIVEL

def eventos_nivel():
    return [
        GRUPO("Inicio de escena", [
            E([al_iniciar()],
              [var_s("Fundido", "=", 1), var_s("FundidoObjetivo", "=", 0),
               var_s("CheckX", "=", f"{V}.X()"), var_s("CheckY", "=", f"{V}.Y()"),
               A("HideLayer", "", '"Dialogo"'), A("HideLayer", "", '"Pausa"'),
               A("Hide", "ZonaDialogo"), tam("Negro", 640, 360)]),
            NOTA("El farol del punto de partida arranca encendido: ahí empieza el recorrido."),
            E([al_iniciar(), si_var_o("FarolGas", "Encendido", "=", 1)],
              [anim("FarolGas", "Encendido")]),
        ], color="nivel"),
        GRUPO("Fundidos", [
            E([], [var_s("Fundido", "+", "(Variable(FundidoObjetivo) - Variable(Fundido)) * min(1, 5 * TimeDelta())"),
                   opacidad("Negro", "=", "Variable(Fundido) * 255")]),
        ], color="nivel"),
        GRUPO("Faroles (checkpoints)", [
            NOTA("Ventura vuelve a encender los faroles de Ambrosio a medida que avanza: cada "
                 "farol encendido es el nuevo punto de reaparición y recupera la vida."),
            E([choca(V, "FarolGas"), anim_es("FarolGas", "Apagado")],
              [anim("FarolGas", "Encendido"), var_s("Faroles", "+", 1),
               var_s("CheckX", "=", "FarolGas.X()"), var_s("CheckY", "=", "FarolGas.Y()"),
               var_o(V, "Vida", "=", VAR("VidaMax")),
               crear("Destello", "FarolGas.X()", "FarolGas.Y() - 50"),
               texto("TextoAviso", '"El farol vuelve a encenderse"'), var_s("AvisoT", "=", 2.2),
               sonido_fx("farol_encendido")]),
        ], color="nivel"),
        GRUPO("Salida del nivel", [
            E([choca(V, "Salida"), si_var_s("Saliendo", "=", 0), si_var_s("Dialogo.Activo", "=", 0)],
              [var_s("Saliendo", "=", 1), var_s("Bloqueado", "=", 1), var_s("FundidoObjetivo", "=", 1),
               sonido_fx("salida")]),
            NOTA("En los tres niveles la salida pasa antes por la pantalla de resultados "
                 "(Resultados = 2 cuando el jugador confirma); el prólogo y la torre van directo."),
            E([si_var_s("Saliendo", "=", 1), si_var_s("Fundido", ">", 0.97),
               O(si_var_s("MostrarResultados", "=", 0), si_var_s("Resultados", "=", 2))],
              [A("Scene", "", "VariableString(Siguiente)", "yes")]),
        ], color="nivel"),
        GRUPO("Resultados del nivel", [
            NOTA("El tiempo corre sólo mientras se juega (sin diálogos, pausa ni salida): no "
                 "se castiga leer la historia."),
            E([si_var_s("Bloqueado", "=", 0), si_var_s("Pausa", "=", 0), si_var_s("Saliendo", "=", 0)],
              [var_s("TiempoNivel", "+", DT)]),
            NOTA("Puntaje: vencer, hacer parry y encender faroles suma; el daño recibido resta, y "
                 "terminar rápido da un bono que se agota a los 300 s. El rango (S, A, B, C) es "
                 "lo que el jugador recuerda, más que el número."),
            E([si_var_s("Saliendo", "=", 1), si_var_s("MostrarResultados", "=", 1),
               si_var_s("Resultados", "=", 0)],
              [var_s("Resultados", "=", 1), var_s("ResultadosT", "=", 0),
               var_s("FundidoObjetivo", "=", 0.7), var_s("Bloqueado", "=", 1),
               var_s("Puntaje", "=", "max(0, Variable(Vencidos) * 100 + Variable(Parries) * 150 "
                                     "+ Variable(Faroles) * 200 + max(0, 3000 - floor(Variable(TiempoNivel)) * 10) "
                                     "- Variable(DanoRecibido) * 5)"),
               texto_s("Rango", '"C"'),
               A("LireFichierExp", '"toonaria"', '"mejor_" + CurrentSceneName()', "", "Mejor"),
               A("ShowLayer", "", '"Resultados"'), sonido_fx("salida")],
              [E([si_var_s("Puntaje", ">=", 2500)], [texto_s("Rango", '"B"')]),
               E([si_var_s("Puntaje", ">=", 3500)], [texto_s("Rango", '"A"')]),
               E([si_var_s("Puntaje", ">=", 4500)], [texto_s("Rango", '"S"')]),
               E([comparar("Variable(Puntaje)", ">", "Variable(Mejor)")],
                 [var_s("Mejor", "=", "Variable(Puntaje)"), var_s("Record", "=", 1),
                  A("EcrireFichierExp", '"toonaria"', '"mejor_" + CurrentSceneName()',
                    "Variable(Puntaje)")]),
               E([], [texto("TituloResultados", '"NIVEL SUPERADO"'),
                      A("SetX", "TituloResultados", "=", "320 - TituloResultados.Width() / 2"),
                      texto("TextoResultados",
                            '"Tiempo: " + ToString(floor(Variable(TiempoNivel))) + " s" + NewLine() + '
                            '"Enemigos vencidos: " + ToString(Variable(Vencidos)) + NewLine() + '
                            '"Parries: " + ToString(Variable(Parries)) + NewLine() + '
                            '"Faroles encendidos: " + ToString(Variable(Faroles)) + NewLine() + '
                            '"Daño recibido: " + ToString(Variable(DanoRecibido)) + NewLine() + NewLine() + '
                            '"PUNTAJE: " + ToString(Variable(Puntaje)) + "     RANGO: " + VariableString(Rango) + NewLine() + '
                            '"Mejor puntaje: " + ToString(Variable(Mejor)) + NewLine() + NewLine() + '
                            '"Enter o tocar: siguiente fase      R: repetir el nivel"')])]),
            E([si_var_s("Resultados", "=", 1)], [var_s("ResultadosT", "+", DT)]),
            E([si_var_s("Resultados", "=", 1), si_var_s("Record", "=", 1)],
              [A("BitmapText::SetTint", "TituloResultados", '"176;133;214"'),
               texto("TituloResultados", '"¡NUEVO RÉCORD!"'),
               A("SetX", "TituloResultados", "=", "320 - TituloResultados.Width() / 2")]),
            NOTA("Medio segundo de espera antes de aceptar la confirmación: si no, el mismo Enter "
                 "que cerró el último diálogo saltaría la pantalla sin que se llegue a leer."),
            E([si_var_s("Resultados", "=", 1), si_var_s("ResultadosT", ">", 0.6),
               O(tecla_recien("Return"), tecla_recien("Space"), C("HasAnyTouchStarted", ""))],
              [var_s("Resultados", "=", 2), var_s("FundidoObjetivo", "=", 1),
               A("HideLayer", "", '"Resultados"'), sonido_fx("menu_ok", 50)]),
            E([si_var_s("Resultados", "=", 1), si_var_s("ResultadosT", ">", 0.6), tecla_recien("r")],
              [A("Scene", "", "CurrentSceneName()", "yes")]),
        ], color="nivel"),
        GRUPO("Pausa", [
            E([O(tecla_recien("Escape"), tecla_recien("p"), tactil_recien("Pausa")),
               si_var_s("Saliendo", "=", 0)],
              [var_s("Pausa", "=", "1 - Variable(Pausa)")]),
            E([si_var_s("Pausa", "=", 1)],
              [A("ChangeTimeScale", "", 0), A("ShowLayer", "", '"Pausa"')]),
            E([si_var_s("Pausa", "=", 0)], [A("HideLayer", "", '"Pausa"')]),
            E([si_var_s("Pausa", "=", 1), tecla_recien("q")],
              [A("ChangeTimeScale", "", 1), cambiar_escena("Titulo")]),
        ], color="nivel"),
    ]


# =================================================================== NIVELES

LEYENDA = """
#  suelo macizo            =  cornisa atravesable      T  tablón podrido (3 celdas)
A  andamio móvil horiz.    V  andamio móvil vertical   N  nube de tinta (sube y baja)
^  rejas con púas          ~  charco de tinta          B  barril
O  toldo elástico          G  caedor de engranajes     F  farol apagado   f farol encendido
r  Repintado    a  Actor    g  Agente    c  Cuervo (en el aire)    p  péndulo (eje)
t  té   l  fragmento luna   P  inicio   S  salida
"""

class Mapa:
    """Grilla del nivel en celdas de 16 px. El piso "normal" tiene su superficie en la fila
    `piso`; los objetos que van apoyados se ponen en la fila de arriba (piso - 1)."""

    def __init__(self, ancho, alto=23, piso=18):
        self.ancho, self.alto, self.piso = ancho, alto, piso
        self.g = [[" "] * ancho for _ in range(alto)]

    def suelo(self, x0, x1, tope=None):
        for y in range(self.piso if tope is None else tope, self.alto):
            for x in range(x0, x1):
                self.g[y][x] = "#"

    def cornisa(self, x0, x1, fila):
        for x in range(x0, x1):
            self.g[fila][x] = "="

    def poner(self, c, x, fila=None):
        self.g[self.piso - 1 if fila is None else fila][x] = c

    def tira(self, c, x0, x1, fila=None):
        for x in range(x0, x1):
            self.poner(c, x, fila)

    def filas(self):
        return ["".join(f) for f in self.g]


def mapa_nivel1():
    """Barrio del Reloj. Cada sección presenta UNA idea nueva y después la combina con las
    anteriores (presentar, practicar, combinar)."""
    m = Mapa(240)
    # 1. La calle del farol (0-40): sin peligro real. Diálogo, un barril para descubrir que
    #    las cartas rompen cosas, una cornisa con premio y el primer Repintado, solo.
    m.suelo(0, 40)
    m.poner("P", 2); m.poner("f", 4); m.poner("D", 13)
    m.poner("B", 20)
    m.cornisa(23, 27, 13); m.poner("l", 25, 12)
    m.poner("r", 33)
    # 2. Primer pozo (40-70): un salto simple, un charco de tinta en el piso y un toldo que
    #    rebota hasta una cornisa alta (premio para el que explora hacia arriba).
    m.suelo(45, 70)
    m.tira("~", 52, 55)
    m.cornisa(48, 53, 13); m.poner("t", 50, 12)
    m.poner("O", 60)
    m.cornisa(62, 67, 8); m.poner("l", 64, 7)
    m.poner("r", 66)
    # 3. Los engranajes del reloj (70-110): checkpoint, engranajes que caen con ritmo
    #    (hay que leer el patrón para pasar) y un pozo chico en el medio.
    m.suelo(70, 84); m.suelo(87, 110)
    m.poner("F", 73)
    for x in (79, 92, 101):
        m.poner("G", x, 3)
    m.cornisa(89, 93, 13)
    m.poner("r", 96); m.poner("r", 105)
    # 4. Rejas con púas (110-140): cuatro celdas de púas que se saltan, con un barril y un
    #    Repintado justo después para castigar el salto apurado.
    m.suelo(110, 140)
    m.tira("^", 117, 121)
    m.poner("B", 127); m.poner("r", 133)
    # 5. El gran pozo (140-158): 288 px imposibles de saltar. Un andamio va y viene; hay que
    #    esperar el momento. La luna arriba premia el riesgo del doble salto.
    m.poner("A", 149, 17)
    m.poner("l", 149, 10)
    # 6. Tablones podridos (158-192): se derrumban al pisarlos, hay que cruzar sin frenar.
    #    Arriba, nubes de tinta que suben y bajan ofrecen una ruta alternativa.
    m.suelo(158, 170)
    for x in range(170, 192, 3):
        m.poner("T", x, 17)
    m.poner("N", 176, 12); m.poner("N", 184, 11); m.poner("l", 184, 9)
    # 7. El último tramo (192-240): checkpoint y tres Repintados con un barril; al final el
    #    farol del puesto de Ambrosio (diálogo) y la reja de salida.
    m.suelo(192, 240)
    m.poner("F", 195)
    m.cornisa(211, 215, 13); m.poner("t", 213, 12)
    m.poner("r", 206); m.poner("B", 214); m.poner("r", 219); m.poner("r", 226)
    m.poner("D", 228); m.poner("F", 231); m.poner("S", 236)
    return m.filas()


NIVEL1 = mapa_nivel1()

DIALOGOS_N1 = {
    "Inicio": ["Ventura|Años después. Otra luna llena, demasiado brillante. Otra vez no.",
               "Ventura|Me llevo el farol de Ambrosio, el de la A grabada. No lo voy a encender... "
               "todavía.",
               "Ventura|Los relojes del barrio marcan cada uno una hora distinta.",
               "Ventura|Hasta el tiempo se corrió de tinta.",
               "Ventura|Ambrosio encendía estos faroles todas las noches. Ahora los enciendo yo."],
    "Final": ["Ventura|El farol del puesto de Ambrosio. Apagado.",
              "Ventura|Y una carta clavada en la madera... morada, con la luna. No es mía.",
              "Ventura|Me está marcando el camino. O me está esperando."],
}


def mapa_prologo():
    """La carpa de Ambrosio (recuerdo). Un circuito de entrenamiento: cada estación enseña una
    sola acción y Ambrosio la presenta con su voz antes de que haga falta."""
    m = Mapa(72)
    m.suelo(0, 72)
    m.poner("P", 3); m.poner("f", 1)
    # Piernas: un cajón bajo (salto corto) y uno más alto (salto completo).
    m.suelo(13, 16, tope=16)
    m.suelo(19, 22, tope=15)
    # Doble salto: la pila de cajones mide 80 px, uno más que el salto completo.
    m.suelo(26, 29, tope=13)
    m.poner("l", 27, 12)
    # Cartas y farol: barriles viejos para romper.
    m.poner("B", 35); m.poner("B", 38)
    m.poner("B", 47); m.poner("B", 49)
    m.poner("t", 54)
    return m.filas()


def mapa_nivel2():
    """Barrio de los Teatros. Presenta al Actor (máscaras que se devuelven con parry), al Cuervo
    y los péndulos de la tramoya, y los combina con lo aprendido en el nivel 1."""
    m = Mapa(256)
    # 1. La calle de los teatros (0-40): el primer Actor, solo, en terreno llano.
    m.suelo(0, 40)
    m.poner("P", 2); m.poner("f", 4)
    m.poner("B", 18)
    m.cornisa(21, 25, 13); m.poner("l", 23, 12)
    m.poner("a", 33)
    # 2. Bolsas de arena (40-76): tres péndulos desfasados sobre piso firme y un pozo chico
    #    al final, para que el ritmo de los péndulos se aprenda sin riesgo de caer.
    m.suelo(40, 66); m.suelo(69, 76)
    for x in (46, 54, 62):
        m.poner("p", x, 10)
    m.poner("t", 58)
    # 3. Marquesinas (76-112): un toldo lleva a una ruta alta con premio; arriba vigilan los
    #    primeros cuervos y abajo patrulla un Repintado.
    m.suelo(76, 112)
    m.poner("O", 82); m.cornisa(84, 92, 9); m.poner("l", 88, 8)
    m.poner("c", 90, 5); m.poner("r", 100); m.poner("c", 106, 6)
    # 4. Tablas del escenario (112-136): tablones podridos sobre el foso, con un cuervo
    #    encima. Del otro lado, farol y un Actor que tira desde terreno firme.
    for x in range(112, 136, 3):
        m.poner("T", x, 17)
    m.poner("c", 124, 5)
    m.suelo(136, 160)
    m.poner("F", 138); m.poner("a", 150)
    # 5. La tramoya (160-186): foso largo que se cruza en dos andamios móviles.
    m.poner("A", 166, 16); m.poner("A", 178, 15)
    m.poner("c", 172, 4)
    # 6. Todo junto (186-222): Repintado, Actor detrás de un barril, péndulo y un toldo
    #    hacia una cornisa con té.
    m.suelo(186, 222)
    m.poner("F", 188)
    m.poner("r", 196); m.poner("B", 203); m.poner("a", 207)
    m.poner("p", 212, 10)
    m.poner("O", 216); m.cornisa(218, 222, 10); m.poner("t", 220, 9)
    # 7. La última función (222-256): un Actor más y, al final, el eco.
    m.suelo(222, 256)
    m.poner("c", 228, 6); m.poner("a", 232)
    m.poner("F", 236)
    m.poner("S", 252)
    return m.filas()


def mapa_nivel3():
    """El Corazón de Toonaria: plaza y torre del reloj. Presenta al Agente y su casco y
    después exige todo lo aprendido, con la escalinata como recorrido vertical."""
    m = Mapa(272)
    # 1. La plaza (0-44): el primer Agente, solo. Barriles con maná para cargar cartas.
    m.suelo(0, 44)
    m.poner("P", 2); m.poner("f", 4)
    m.poner("B", 16)
    m.cornisa(20, 24, 13); m.poner("l", 22, 12)
    m.poner("g", 32)
    # 2. Péndulos de reloj y engranajes (48-84), después de un pozo corto.
    m.suelo(48, 84)
    m.poner("p", 56, 10); m.poner("p", 66, 10)
    m.poner("G", 61, 3); m.poner("G", 73, 3)
    m.poner("r", 79)
    # 3. Nubes de tinta (84-116): un foso de 512 px que sólo se cruza saltando de nube en nube,
    #    con un cuervo arriba.
    for x, fila in ((88, 14), (95, 12), (102, 13), (109, 14)):
        m.poner("N", x, fila)
    m.poner("c", 99, 4)
    # 4. La escalinata (116-152): farol, escalones de una celda y un descanso alto con un
    #    Agente y un Actor; se baja de un salto.
    m.suelo(116, 152)
    m.poner("F", 118)
    for k, x in enumerate(range(124, 134, 2)):
        m.suelo(x, x + 2, tope=17 - k)
    m.suelo(134, 150, tope=13)
    m.poner("g", 140, 12); m.poner("a", 146, 12)
    m.poner("l", 136, 11)
    # 5. Rejas, péndulo y cuervos (152-196).
    m.suelo(152, 196)
    m.tira("^", 158, 162)
    m.poner("p", 168, 10)
    m.poner("g", 177); m.poner("c", 182, 5)
    m.tira("^", 186, 189)
    m.poner("t", 192)
    # 6. La última prueba (196-240): tablones sobre el foso con un cuervo, farol y el grupo
    #    final de enemigos (Agente, Actor sobre un cajón, Repintado).
    for x in range(196, 214, 3):
        m.poner("T", x, 17)
    m.poner("c", 205, 5)
    m.suelo(214, 240)
    m.poner("F", 216)
    m.poner("g", 224)
    m.suelo(228, 235, tope=15); m.poner("a", 231, 14)
    m.poner("r", 238)
    # 7. La puerta de la torre (240-272): escalones finales y el diálogo antes de entrar.
    m.suelo(240, 272)
    for k, x in enumerate(range(246, 252, 2)):
        m.suelo(x, x + 2, tope=17 - k)
    m.suelo(252, 272, tope=15)
    m.poner("F", 254, 14)
    return m.filas()


def mapa_arena():
    """Cima de la torre: una sola pantalla. Dos cornisas altas a los costados (se llega con
    doble salto) sirven de refugio contra la embestida; desde ahí arriba las cartas pasan por
    encima del jefe, así que para pegarle hay que volver a bajar."""
    m = Mapa(40)
    m.suelo(0, 40)
    m.poner("P", 6)
    m.cornisa(3, 10, 11); m.cornisa(30, 37, 11)
    return m.filas()


NIVEL2 = mapa_nivel2()
NIVEL3 = mapa_nivel3()
PROLOGO = mapa_prologo()
ARENA = mapa_arena()

DIALOGOS_PROLOGO = {
    "Inicio": ["Ambrosio|De nuevo. Cortá, cargá, soltá. En ese orden, no al revés.",
               "Ventura|Ya sé, ya sé. Primero las piernas, después las cartas.",
               "Ambrosio|Entonces mostrame las piernas. Cruzá el circuito. "
               "(Flechas o A / D para moverte, Espacio para saltar)",
               "Ambrosio|Si mantenés apretado el salto, llegás más alto. Si lo tocás, saltás bajito."],
    "Doble": ["Ambrosio|Esa pila no la saltás de una.",
              "Ambrosio|Saltá, y cuando estés arriba de todo, saltá otra vez. "
              "El aire también se pisa. (Espacio en el aire)"],
    "Cartas": ["Ambrosio|Ahora el mazo. Esos barriles viejos no le importan a nadie.",
               "Ambrosio|Mantené apretado para cargar y soltá para tirar. "
               "Cuanto más aguantás, más fuerte sale. (X o J)",
               "Ventura|¿Y si la suelto enseguida?",
               "Ambrosio|Sale igual, pero débil. Hay cosas que una carta débil ni raspa."],
    "Farol": ["Ambrosio|Y cuando las cartas no alcancen, el farol. Arde fuerte, pero cuesta. (C o K)",
              "Ambrosio|No lo gastes en barriles... Bueno, en estos sí."],
    "Parry": ["Ambrosio|Lo último, y lo más difícil. Te voy a tirar una carta.",
              "Ambrosio|Cuando esté por tocarte, la devolvés. Ni antes ni después. "
              "(Z o L, justo antes del golpe)",
              "Ventura|¿Y si me pega?",
              "Ambrosio|Te va a doler un poquito. Por eso se aprende."],
    "ParryBien": ["Ambrosio|¡Eso! Lo que te tiran, lo devolvés. Así se pelea contra la luna."],
    "Final": ["Ambrosio|Ventura. Una sola regla, más importante que todas las que te enseñé "
              "con las cartas.",
              "Ventura|¿Cuál?",
              "Ambrosio|A la luna llena la mirás una vez, para saber que salió. Después, al piso. "
              "Por más brillante que se ponga.",
              "Ventura|¿Y si me gusta mirarla? En la carta, digo. Reflejada en la laca se ve linda.",
              "Ambrosio|En la carta mirala todo lo que quieras. Al cielo, una vez.",
              "Ambrosio|Y esperá que alguien te enseñe a vos lo que te estoy enseñando yo ahora."],
}

DIALOGOS_N2 = {
    "Inicio": ["Ventura|El barrio de los teatros. Las marquesinas anuncian obras que nunca se "
               "estrenaron.",
               "Ventura|Y los actores siguen actuando, aunque ya no quede público.",
               "Ventura|Si me tiran algo, se lo devuelvo. Como en la carpa."],
    "Final": ["Actor|Cortá... cargá... soltá. Cortá, cargá, soltá. En ese orden, no al revés.",
              "Ventura|...Eso lo decía Ambrosio.",
              "Actor|Cortá, cargá, soltá. Cortá, cargá...",
              "Ventura|No sabe que lo está repitiendo. Lo escuchó tantas noches que se le quedó "
              "pegado.",
              "Ventura|Ambrosio pasó por acá. Sigo."],
}

DIALOGOS_N3 = {
    "Inicio": ["Ventura|El corazón de Toonaria. Todo plateado.",
               "Ventura|Hasta los guardias del reloj están repintados. Y siguen haciendo la ronda.",
               "Ventura|Con esos cascos, una carta suelta no va a alcanzar. Hay que cargar."],
    "Final": ["Ventura|Huellas de garras. Sobre tinta fresca.",
              "Ventura|(Ventura enciende el farol con la A grabada.)",
              "Ventura|A la luna se la mira una vez."],
}

DIALOGOS_ARENA = {
    "Encuentro": ["Ventura|Ambrosio.",
                  "Ambrosio|(Gruñe. No hay nada humano en los ojos.)",
                  "Ventura|(bajo, casi para sí) Cortá, cargá, soltá."],
    "Transicion": ["Ambrosio|Ven... tura... no me mires así...",
                   "Ventura|¡Ambrosio! Sé que estás ahí adentro.",
                   "Ambrosio|¡Andate! La luna... ¡la luna no me suelta!"],
    "Final": ["Ambrosio|Te dije que practicaras el remate. Nunca me hiciste caso.",
              "Ventura|Te hice caso en todo lo demás.",
              "Ambrosio|¿Cómo seguís siendo vos?",
              "Ventura|Nunca la miré. Ni una vez, como decías vos.",
              "Ambrosio|Yo tampoco la miraba. La miré una sola vez de más.",
              "Ventura|Yo la leo en la carta. Siempre. Al reflejo, en la laca. Como me enseñaste "
              "a leer la suerte.",
              "Ventura|Nunca me diste la regla completa. Me diste el oficio. Y el oficio me salvó.",
              "Ambrosio|La próxima luna no va a preguntar quién fui antes. Andate de acá. Ahora "
              "que podés.",
              "Ventura|..."],
}


def construir_mapa(mapa, escena_nombre, tiles, nivel_alto):
    """Convierte el mapa de texto en instancias. Devuelve (instancias, pos_inicio)."""
    filas = [f.ljust(max(len(x) for x in mapa)) for f in mapa]
    alto, ancho_ = len(filas), len(filas[0])
    inst = []
    inicio = (64, 200)
    ocupado = [[c == "#" for c in f] for f in filas]
    # Suelo: rectángulos máximos por corridas horizontales que se repiten hacia abajo.
    visto = [[False] * ancho_ for _ in range(alto)]
    for y in range(alto):
        x = 0
        while x < ancho_:
            if ocupado[y][x] and not visto[y][x]:
                x1 = x
                while x1 < ancho_ and ocupado[y][x1] and not visto[y][x1]:
                    x1 += 1
                y1 = y + 1
                while y1 < alto and all(ocupado[y1][k] and not visto[y1][k] for k in range(x, x1)):
                    y1 += 1
                # el último bloque se estira hasta más allá del borde inferior de la pantalla
                extra = 40 if y1 == alto else 0
                inst.append(instancia("Suelo", x * CELDA, y * CELDA, z=2,
                                      w=(x1 - x) * CELDA, h=(y1 - y) * CELDA + extra))
                for yy in range(y, y1):
                    for xx in range(x, x1):
                        visto[yy][xx] = True
                x = x1
            else:
                x += 1
    # Borde de adoquines sobre toda superficie expuesta.
    for y in range(alto):
        x = 0
        while x < ancho_:
            if ocupado[y][x] and (y == 0 or not ocupado[y - 1][x]):
                x1 = x
                while x1 < ancho_ and ocupado[y][x1] and (y == 0 or not ocupado[y - 1][x1]):
                    x1 += 1
                inst.append(instancia("Borde", x * CELDA, y * CELDA - 2, z=3,
                                      w=(x1 - x) * CELDA, h=14))
                x = x1
            else:
                x += 1
    for y, fila in enumerate(filas):
        x = 0
        while x < ancho_:
            c = fila[x]
            px, py = x * CELDA, y * CELDA
            base = py + CELDA  # los objetos "apoyados" tienen el origen en los pies
            if c == "=":
                x1 = x
                while x1 < ancho_ and fila[x1] == "=":
                    x1 += 1
                inst.append(instancia("Cornisa", px, py + 6, z=3, w=(x1 - x) * CELDA, h=10))
                x = x1
                continue
            if c == "^":
                x1 = x
                while x1 < ancho_ and fila[x1] == "^":
                    x1 += 1
                inst.append(instancia("Rejas", px, base - 20, z=4, w=(x1 - x) * CELDA, h=20))
                x = x1
                continue
            if c == "~":
                x1 = x
                while x1 < ancho_ and fila[x1] == "~":
                    x1 += 1
                for k in range(x, x1, 3):
                    inst.append(instancia("CharcoTinta", k * CELDA + 24, base - 1, z=4))
                x = x1
                continue
            if c == "T":
                # el borde superior del tablón queda a la misma altura que el piso de la fila
                inst.append(instancia("Tablon", px, py + 16, z=3))
                x += 1
                continue
            simple = {
                "P": None, "r": ("Repintado", px + 8, base), "a": ("Actor", px + 8, base),
                "g": ("Agente", px + 8, base), "c": ("Cuervo", px + 8, py + 8),
                "p": ("Pendulo", px + 8, py),
                "f": ("FarolGas", px + 8, base), "F": ("FarolGas", px + 8, base),
                "t": ("Te", px + 8, base - 2), "l": ("Luna", px + 8, base - 4),
                "B": ("Barril", px + 8, base), "O": ("Toldo", px + 8, base),
                "G": ("Caedor", px + 8, py), "A": ("Andamio", px + 8, py + 16),
                "V": ("Andamio", px + 8, py + 16), "N": ("NubeTinta", px + 8, py + 8),
                "S": ("Salida", px + 8, base),
            }
            if c == "P":
                inicio = (px + 8, base)
            elif c == "D":
                pass  # las zonas de diálogo se crean aparte, con su Id
            elif c in simple:
                nombre, ix, iy = simple[c]
                vars_ = None
                if c == "V":
                    vars_ = {"DX": 0, "DY": 60, "Vel": 1.1}
                if c == "A":
                    vars_ = {"DX": 88, "DY": 0, "Vel": 0.9, "Fase": x * 0.6}
                if c == "p":
                    vars_ = {"Fase": x * 0.9}
                if c == "N":
                    vars_ = {"DY": 26, "Fase": x * 0.7}
                if c == "G":
                    vars_ = {"T": (x % 5) * 0.4}
                if c == "f":
                    vars_ = {"Encendido": 1}
                inst.append(instancia(nombre, ix, iy, z=5, vars_=vars_))
            x += 1
    return inst, inicio, ancho_ * CELDA


def escena_nivel(nombre, mapa, prefijo_arte, dialogos, siguiente, zonas_dialogo,
                 prefijo_tiles=None, interior=False, objetos_extra=(), inst_extra=(),
                 enlaces_extra=(), vars_extra=None, eventos_extra=(), tema=None,
                 resultados=False):
    """Escena de juego. Los interiores (carpa, cima de la torre) no tienen cielo, nubes ni
    bruma: los objetos existen igual (las hojas de eventos compartidas los nombran) pero sin
    instancias, así que esas acciones no hacen nada en esas escenas."""
    tiles = PX / "tiles"
    fondos = PX / "fondos"
    pt = prefijo_tiles or prefijo_arte
    pf = "n1" if interior else prefijo_arte
    objetos = [
        mosaico(rec, "Suelo", tiles / f"{pt}_suelo.png", 32, 32,
                comportamientos=[plataforma()]),
        mosaico(rec, "Borde", tiles / f"{pt}_borde.png", 32, 14),
        mosaico(rec, "Cornisa", tiles / f"{pt}_cornisa.png", 32, 10,
                comportamientos=[plataforma("Jumpthru")]),
        sprite(rec, "FondoCielo", [("Default", [fondos / f"{pf}_cielo.png"], 1, False)],
               origen=(0, 0)),
        sprite(rec, "FondoCiudad", [("Default", [fondos / f"{prefijo_arte}_ciudad.png"], 1, False)],
               origen=(0, 0)),
        mosaico(rec, "NubesLejos", fondos / f"{pf}_nubes_lejos.png", 640, 90),
        mosaico(rec, "NubesCerca", fondos / f"{pf}_nubes_cerca.png", 960, 130),
        mosaico(rec, "Bruma", fondos / f"{pf}_bruma.png", 640, 48),
        # Paredes invisibles en los dos bordes del nivel: sin esto se podía caminar fuera del
        # mapa y caer al vacío por el costado.
        sprite(rec, "Limite", [("Default", [PX / "hud" / "Negro.png"], 1, False)], origen=(0, 0),
               comportamientos=[plataforma()]),
        *objetos_extra,
    ]
    inst, (px, py), nivel_ancho = construir_mapa(mapa, nombre, tiles, H)
    nivel_alto = H
    fondo_w, fondo_h = tamano(fondos / f"{prefijo_arte}_ciudad.png")
    factor_x = max(0.0, (fondo_w - W) / max(1, nivel_ancho - W))
    capas = [capa("Cielo"), capa("NubesL"), capa("Ciudad"), capa("NubesC"), capa(""),
             capa("Frente"), capa("HUD"), capa("Tactil"), capa("Dialogo"), capa("Pausa"),
             capa("Transicion"), capa("Resultados")]
    if not interior:
        inst += [
            instancia("FondoCielo", 0, 0, "Cielo"),
            instancia("NubesLejos", 0, 20, "NubesL", w=W, h=90),
            instancia("NubesCerca", 0, 0, "NubesC", w=W, h=130),
            instancia("Bruma", 0, 236, "NubesC", w=W, h=48),
        ]
    inst += [
        instancia("FondoCiudad", 0, 0, "Ciudad"),
        instancia("Limite", -16, -400, "", w=16, h=H + 800),
        instancia("Limite", nivel_ancho, -400, "", w=16, h=H + 800),
        instancia(V, px, py, "", z=10),
        instancia("Retrato", 8, 8, "HUD"),
        instancia("BarraManaFondo", 40, 27, "HUD"),
        instancia("BarraMana", 43, 29, "HUD", w=58, h=4),
        instancia("BarraCargaFondo", 0, 0, "", z=20), instancia("BarraCarga", 0, 0, "", z=21),
        instancia("FondoAviso", 220, 42, "HUD", z=0, w=200, h=20),
        instancia("TextoAviso", 320, 46, "HUD", z=1),
        instancia("CajaDialogo", 20, 272, "Dialogo", w=600, h=76),
        instancia("RetratoDialogo", 30, 284, "Dialogo"),
        instancia("NombreDialogo", 70, 282, "Dialogo"),
        # Con ancho propio el texto bitmap corta las líneas largas dentro de la caja.
        instancia("TextoDialogo", 70, 298, "Dialogo", w=528, h=44),
        instancia("Seguir", 600, 334, "Dialogo"),
        instancia("TextoPausa", 320, 150, "Pausa"),
        instancia("Negro", 0, 0, "Transicion", w=W, h=H),
        instancia("Blanco", 0, 0, "Transicion", z=1, w=W, h=H),
        instancia("CajaDialogo", 130, 60, "Resultados", w=380, h=230),
        instancia("TituloResultados", 320, 74, "Resultados"),
        instancia("TextoResultados", 152, 116, "Resultados"),
        *inst_extra,
    ]
    inst += [instancia("CartaVida", 40 + i * 13, 10, "HUD", vars_={"Indice": i}) for i in range(5)]
    # Botones táctiles: dirección abajo a la izquierda (pulgar izquierdo) y acciones abajo a la
    # derecha, con saltar en la posición más cómoda del pulgar derecho; pausa arriba, lejos de
    # los toques del juego.
    botones_ = {"Izq": (14, 300), "Der": (66, 300), "Saltar": (586, 300), "Carta": (534, 312),
                "Parry": (586, 248), "Farol": (534, 260), "Pausa": (590, 8)}
    for tipo, (bx, by) in botones_.items():
        inst.append(instancia("BotonTactil", bx, by, "Tactil", w=44 if tipo != "Pausa" else 36,
                              h=44 if tipo != "Pausa" else 36, vars_={"Tipo": tipo}))
    for (zx, zid, despues) in zonas_dialogo:
        inst.append(instancia("ZonaDialogo", zx, 0, "", w=24, h=H,
                              vars_={"Id": zid, "Despues": despues}))
    variables_ = {
        "NivelAncho": nivel_ancho, "NivelAlto": nivel_alto, "CheckX": px, "CheckY": py,
        "CamX": px, "CamY": py, "Temblor": 0, "Hitstop": 0, "Fundido": 1, "FundidoObjetivo": 0,
        "Siguiente": siguiente, "Saliendo": 0, "Pausa": 0, "Bloqueado": 0, "Tiempo": 0,
        "AvisoT": 0, "SinSonido": 0, "AvisoCasco": 0, "Parries": 0, "RetratoAmbrosio": "Ambrosio",
        "Tactil": {**{b: 0 for b in BOTONES_TACTILES}, **{f"{b}Recien": 0 for b in BOTONES_TACTILES}},
        "MiraCam": 1, "Flash": 0, "MostrarResultados": 1 if resultados else 0, "Resultados": 0,
        "ResultadosT": 0, "TiempoNivel": 0, "Vencidos": 0, "Faroles": 0, "DanoRecibido": 0,
        "Puntaje": 0, "Mejor": 0, "Record": 0, "Rango": "C",
        "FactorCieloX": round(factor_x * 0.25, 4), "FactorCieloY": 0,
        "FactorCiudadX": round(factor_x, 4), "FactorCiudadY": 0,
        "Dialogo": {"Activo": 0, "Indice": 0, "Chars": 0, "Avanzo": 0, "Set": "", "Linea": "",
                    "Despues": ""},
        "Guion": {k: v for k, v in dialogos.items()},
        **(vars_extra or {}),
    }
    eventos = [
        NOTA(f"{nombre}: la lógica compartida está en los eventos externos enlazados abajo. "
             "Acá sólo va lo propio de esta escena."),
        E([al_iniciar()], [texto("TextoPausa", lineas("PAUSA", "", "Esc o II: seguir", "Q: volver al título")),
                           A("Hide", "Limite"), A("HideLayer", "", '"Resultados"'),
                           opacidad("Blanco", "=", 0),
                           musica(tema) if tema else parar_musica()]),
        *eventos_extra,
        ENLACE("Tactil"), ENLACE("Nivel"), ENLACE("Jugador"), ENLACE("Combate"), ENLACE("Enemigos"),
        ENLACE("Obstaculos"), *[ENLACE(e) for e in enlaces_extra],
        ENLACE("Dialogo"), ENLACE("Camara"), ENLACE("HUD"),
    ]
    return escena(nombre, capas, objetos, inst, eventos, variables_)


def iniciar_dialogo(conjunto, despues=""):
    """Las mismas acciones que dispara una ZonaDialogo, para diálogos que arrancan por un
    hecho del juego (el jefe cambia de fase, Ambrosio ve el parry) y no por un lugar."""
    return [texto_s("Dialogo.Set", f'"{conjunto}"'), texto_s("Dialogo.Despues", f'"{despues}"'),
            var_s("Dialogo.Activo", "=", 1), var_s("Dialogo.Indice", "=", 0),
            var_s("Dialogo.Chars", "=", 0), var_s("Bloqueado", "=", 1),
            var_o(V, "Cargando", "=", 0), A("ShowLayer", "", '"Dialogo"')]


# =================================================================== PRÓLOGO

def objetos_prologo():
    am = PX / "ambrosio"
    return [
        sprite(rec, "Ambrosio",
               anims_carpeta(am, [("Idle", "Idle", 0.18, True), ("Farol", "Farol", 1, False),
                                  ("Caminar", "Caminar", 1, False)]),
               origen=(48, 62)),
        sprite(rec, "Barrera", [("Default", [PX / "hud" / "Negro.png"], 1, False)], origen=(0, 0),
               comportamientos=[plataforma()]),
    ]


def eventos_prologo():
    AM = "Ambrosio"
    return [
        GRUPO("Ambrosio", [
            NOTA("Ambrosio siempre mira a Ventura. Cuando ella deja atrás la primera estación, "
                 "él ya la está esperando en la última (se mueve fuera de cámara)."),
            E([al_iniciar()], [A("Hide", "Barrera")]),
            E([C("PosX", AM, ">", f"{V}.X()")], [voltear(AM, True)]),
            E([C("PosX", AM, "<=", f"{V}.X()")], [voltear(AM, False)]),
            E([si_var_s("Movido", "=", 0), C("PosX", V, ">", 33 * CELDA)],
              [A("SetXY", AM, "=", 64 * CELDA + 8, "=", 18 * CELDA), var_s("Movido", "=", 1)]),
            E([si_var_s("GestoT", ">", 0)], [var_s("GestoT", "-", DT), anim(AM, "Farol")]),
            E([si_var_s("GestoT", "<=", 0)], [anim(AM, "Idle")]),
        ], color="nivel"),
        GRUPO("Lección de parry", [
            NOTA("Ambrosio tira cartas lentas (garras de luna de práctica, 4 de daño) hasta que "
                 "Ventura devuelve una. Una barrera invisible impide seguir sin aprender el "
                 "parry: es la mecánica que decide la pelea final."),
            E([si_var_s("Leccion", "=", 0),
               C("StringObjectVariable", "ZonaDialogo", "Id", "=", '"Parry"'),
               si_var_o("ZonaDialogo", "Visto", "=", 1), si_var_s("Dialogo.Activo", "=", 0)],
              [var_s("Leccion", "=", 1), var_s("TiroT", "=", 0.8)]),
            E([si_var_s("Leccion", "=", 1)], [var_s("TiroT", "-", DT)]),
            E([si_var_s("Leccion", "=", 1), si_var_s("TiroT", "<=", 0)],
              [crear("GarraLuna", f"{AM}.X() - 20", f"{AM}.Y() - 24"),
               var_o("GarraLuna", "Dir", "=", -1), var_o("GarraLuna", "Vel", "=", 120),
               var_o("GarraLuna", "Dano", "=", 4), var_s("TiroT", "=", 2.4),
               var_s("GestoT", "=", 0.4), sonido_fx("garra", 40)]),
            E([si_var_s("Leccion", "=", 1), si_var_s("Parries", ">=", 1)],
              [var_s("Leccion", "=", 2), borrar("Barrera"), *iniciar_dialogo("ParryBien")]),
            E([choca("GarraLuna", AM), si_var_o("GarraLuna", "Reflejada", "=", 1)],
              [crear("Destello", "GarraLuna.X()", "GarraLuna.Y()"), borrar("GarraLuna")]),
        ], color="nivel"),
    ]


# =================================================================== JEFE

def objetos_jefe():
    lo = PX / "lobo"
    f = lambda p: frames_de(lo, p)  # noqa: E731
    lobo = sprite(
        rec, "Lobo",
        [("Idle", f("Idle"), 0.14, True), ("Acechar", f("Acechar"), 0.12, True),
         ("PrepararEmbestida", f("PrepararEmbestida"), 0.2, True),
         ("Embestida", f("Embestida"), 0.08, True), ("Atascado", f("Atascado"), 1, False),
         ("Liberarse", f("Liberarse"), 1, False),
         ("ZarpazoAviso", f("Zarpazo")[0:1], 1, False), ("ZarpazoGolpe", f("Zarpazo")[1:3], 0.12, False),
         ("AullidoAviso", f("Aullido")[1:2], 1, False),
         ("AullidoGolpe", [f("Aullido")[0], f("Aullido")[2]], 0.3, False),
         ("GarraAviso", f("GarraLuna")[0:1], 1, False), ("GarraTiro", f("GarraLuna")[1:3], 0.14, False),
         ("Transicion", f("Transicion"), 0.16, True), ("Golpeado", f("Golpeado"), 0.1, False),
         ("Derrota", f("Derrota"), 0.4, False)],
        origen=(96, 126), mascara=(70, 50, 120, 126),
        vars_={"Vida": 320, "VidaMax": 320, "Estado": "espera", "T": 0, "Dir": -1, "Fase": 1,
               "Paso": 0, "Golpe": 0, "Disparos": 0, "Ritmo": 1, "Vel": 0})
    h = PX / "hud"
    return [
        lobo,
        sprite(rec, "BarraJefeFondo", [("Default", frames_de(h, "BarraJefeFondo"), 1, False)], origen=(0, 0)),
        sprite(rec, "BarraJefe", [("Default", frames_de(h, "BarraJefe"), 1, False)], origen=(0, 0)),
        bitmap("NombreJefe", "Ambrosio, el Farolero", alinear="center", tinte="176;133;214"),
    ]


def eventos_jefe():
    L = "Lobo"
    def es(e, neg=False):
        return estado_es(L, e, neg)

    def a(e):
        return poner_estado(L, e)

    siguiente_paso = var_o(L, "Paso", "=", f"mod({L}.Variable(Paso) + 1, {L}.Variable(Fase) + 1)")
    mirar = var_o(L, "Dir", "=", f"sign({V}.X() - {L}.X() + 0.01)")
    activo = [si_var_s("Pelea", "=", 1), es("transicion", True), es("derrota", True), es("espera", True)]
    golpeable = [si_var_o(V, "Invulnerable", "<=", 0), si_var_o(V, "Muerto", "=", 0),
                 si_var_o(V, "ParryVentana", "<=", 0)]
    return [
        GRUPO("Jefe: comienzo de la pelea", [
            NOTA("La pelea arranca cuando termina el diálogo del encuentro (la zona de diálogo "
                 "está en el punto de partida, así que se dispara en el primer cuadro)."),
            E([al_iniciar()], [A("Hide", "BarraJefeFondo"), A("Hide", "BarraJefe"),
                               A("Hide", "NombreJefe"), voltear(L, True)]),
            E([si_var_s("Pelea", "=", 0), si_var_s("Dialogo.Activo", "=", 1)], [var_s("Encuentro", "=", 1)]),
            E([si_var_s("Pelea", "=", 0), si_var_s("Encuentro", "=", 1), si_var_s("Dialogo.Activo", "=", 0)],
              [var_s("Pelea", "=", 1), a("decidir"), var_o(L, "T", "=", 1.0),
               A("Show", "BarraJefeFondo", ""), A("Show", "BarraJefe", ""), A("Show", "NombreJefe", ""),
               var_s("Temblor", "=", 5), sonido_fx("aullido", 70), musica("jefe", 50)]),
            E([si_var_s("Pelea", "=", 0)], [anim(L, "Idle")]),
        ], color="jefe"),
        GRUPO("Jefe: ciclo de ataques", [
            NOTA("Pelea por patrones, no reactiva: cada fase repite un ciclo FIJO (Paso). Fase 1: "
                 "Embestida, Zarpazo. Fase 2: Embestida, Garra de luna, Aullido. Lo único que "
                 "cambia con la vida que le queda es el Ritmo: en la fase 2 los avisos se acortan "
                 "hasta un 60 %, sin cambiar el orden, así el jugador puede aprenderlo."),
            E([si_var_o(L, "Fase", "=", 2)],
              [var_o(L, "Ritmo", "=", f"clamp(0.6 + 0.4 * {L}.Variable(Vida) / ({L}.Variable(VidaMax) * 0.5), 0.6, 1)")]),
            E([es("decidir")], [var_o(L, "T", "-", DT), anim(L, "Idle"), mirar]),
            E([es("decidir"), si_var_o(L, "T", "<=", 0), si_var_o(L, "Paso", "=", 0)],
              [a("aviso_embestida"), var_o(L, "T", "=", f"1.0 * {L}.Variable(Ritmo) - ({L}.Variable(Fase) - 1) * 0.2"),
               anim(L, "PrepararEmbestida"), sonido_fx("grunido", 60)]),
            E([es("decidir"), si_var_o(L, "T", "<=", 0), si_var_o(L, "Fase", "=", 1), si_var_o(L, "Paso", "=", 1)],
              [a("acercarse"), var_o(L, "T", "=", 1.6)]),
            E([es("decidir"), si_var_o(L, "T", "<=", 0), si_var_o(L, "Fase", "=", 2), si_var_o(L, "Paso", "=", 1)],
              [a("aviso_garra"), var_o(L, "T", "=", f"0.7 * {L}.Variable(Ritmo)"), anim(L, "GarraAviso"),
               sonido_fx("garra_carga", 55)]),
            E([es("decidir"), si_var_o(L, "T", "<=", 0), si_var_o(L, "Fase", "=", 2), si_var_o(L, "Paso", "=", 2)],
              [a("aviso_aullido"), var_o(L, "T", "=", f"0.8 * {L}.Variable(Ritmo)"), anim(L, "AullidoAviso"),
               sonido_fx("grunido", 60)]),
        ], color="jefe"),
        GRUPO("Jefe: Embestida", [
            NOTA("Aviso agachado, carrera en línea recta hasta la pared y queda atascado: esa "
                 "es la ventana de castigo (las cartas hacen 50 % más de daño mientras dura)."),
            E([es("aviso_embestida")], [var_o(L, "T", "-", DT)]),
            E([es("aviso_embestida"), si_var_o(L, "T", "<=", 0)],
              [a("embestida"), mirar, anim(L, "Embestida"),
               var_o(L, "Vel", "=", f"300 + ({L}.Variable(Fase) - 1) * 70"),
               var_s("Temblor", "=", 2), sonido_fx("embestida", 60)]),
            E([es("embestida")], [A("SetX", L, "+", f"{L}.Variable(Dir) * {L}.Variable(Vel) * {DT}")]),
            E([es("embestida"), O(C("PosX", L, "<", 70), C("PosX", L, ">", "Variable(NivelAncho) - 70"))],
              [A("SetX", L, "=", f"clamp({L}.X(), 70, Variable(NivelAncho) - 70)"),
               a("atascado"), var_o(L, "T", "=", f"1.5 - ({L}.Variable(Fase) - 1) * 0.4"),
               anim(L, "Atascado"), var_s("Temblor", "=", 7),
               crear("Polvo", f"{L}.X() + {L}.Variable(Dir) * 30", f"{L}.Y()"),
               sonido_fx("golpe_pared", 70)]),
            *cuenta_regresiva(L, "atascado", "liberarse", 0.35, [anim(L, "Liberarse")]),
            *cuenta_regresiva(L, "liberarse", "decidir", 0.7, [siguiente_paso]),
        ], color="jefe"),
        GRUPO("Jefe: Zarpazo", [
            NOTA("Cuerpo a cuerpo de arco corto: se acerca acechando, levanta la garra (aviso) y "
                 "golpea. Si se le hace parry al zarpazo queda aturdido un segundo."),
            E([es("acercarse")], [var_o(L, "T", "-", DT), mirar, anim(L, "Acechar"),
                                  A("SetX", L, "+", f"{L}.Variable(Dir) * 110 * {DT}")]),
            E([es("acercarse"), O(comparar(f"abs({V}.X() - {L}.X())", "<", 100), si_var_o(L, "T", "<=", 0))],
              [a("aviso_zarpazo"), var_o(L, "T", "=", f"0.55 * {L}.Variable(Ritmo)"),
               anim(L, "ZarpazoAviso"), sonido_fx("grunido", 50)]),
            E([es("aviso_zarpazo")], [var_o(L, "T", "-", DT)]),
            E([es("aviso_zarpazo"), si_var_o(L, "T", "<=", 0)],
              [a("zarpazo"), var_o(L, "T", "=", 0.45), anim(L, "ZarpazoGolpe"),
               crear("Zarpazo", f"{L}.X() + {L}.Variable(Dir) * 52", f"{L}.Y() - 46"),
               escala("Zarpazo", "=", 3), sonido_fx("zarpazo", 65)]),
            E([es("zarpazo")], [var_o(L, "T", "-", DT),
                                A("SetX", L, "+", f"{L}.Variable(Dir) * 70 * {DT}")]),
            E([si_var_o(V, "ParryVentana", ">", 0), choca(V, "Zarpazo"), es("zarpazo")],
              [borrar("Zarpazo"), a("aturdido"), var_o(L, "T", "=", 1.0), anim(L, "Atascado"),
               *efecto_parry(),
               var_o(V, "Mana", "+", 20), var_s("Hitstop", "=", 8), var_s("Temblor", "=", 4),
               var_s("Parries", "+", 1), sonido_fx("parry")]),
            E([*golpeable, choca(V, "Zarpazo"), es("zarpazo")],
              [var_o(V, "Dano", "=", 20), var_o(V, "EmpujeDir", "=", f"{L}.Variable(Dir)")]),
            *cuenta_regresiva(L, "zarpazo", "decidir", f"0.8 * {L}.Variable(Ritmo)", [siguiente_paso]),
            *cuenta_regresiva(L, "aturdido", "decidir", 0.5, [siguiente_paso]),
        ], color="jefe"),
        GRUPO("Jefe: Garra de luna", [
            NOTA("Tres garras moradas a la altura del pecho, una cada 0,32 s. Se saltan o se "
                 "devuelven con parry: devuelta, cada una le saca 40 de vida al jefe."),
            E([es("aviso_garra")], [var_o(L, "T", "-", DT)]),
            E([es("aviso_garra"), si_var_o(L, "T", "<=", 0)],
              [a("garra"), var_o(L, "Disparos", "=", 3), var_o(L, "T", "=", 0), anim(L, "GarraTiro")]),
            E([es("garra")], [var_o(L, "T", "-", DT)]),
            E([es("garra"), si_var_o(L, "T", "<=", 0), si_var_o(L, "Disparos", ">", 0)],
              [crear("GarraLuna", f"{L}.X() + {L}.Variable(Dir) * 40", f"{L}.Y() - 26"),
               var_o("GarraLuna", "Dir", "=", f"{L}.Variable(Dir)"), var_o("GarraLuna", "Vel", "=", 200),
               var_o("GarraLuna", "Dano", "=", 18), var_o(L, "Disparos", "-", 1),
               var_o(L, "T", "=", 0.32), sonido_fx("garra", 55)]),
            E([es("garra"), si_var_o(L, "T", "<=", 0), si_var_o(L, "Disparos", "=", 0)],
              [a("decidir"), var_o(L, "T", "=", f"0.9 * {L}.Variable(Ritmo)"), siguiente_paso]),
        ], color="jefe"),
        GRUPO("Jefe: Aullido", [
            NOTA("Se para en dos patas y aúlla: dos ondas de luz de luna corren por el piso hacia "
                 "los dos lados. Alcanzan las paredes, así que alejarse no alcanza: hay que saltarlas."),
            E([es("aviso_aullido")], [var_o(L, "T", "-", DT)]),
            E([es("aviso_aullido"), si_var_o(L, "T", "<=", 0)],
              [a("aullido"), var_o(L, "T", "=", 1.0), anim(L, "AullidoGolpe"),
               crear("OndaLuna", f"{L}.X() + 30", f"{L}.Y()"), var_o("OndaLuna", "Dir", "=", 1),
               crear("OndaLuna", f"{L}.X() - 30", f"{L}.Y()"), var_o("OndaLuna", "Dir", "=", -1),
               var_s("Temblor", "=", 8), sonido_fx("aullido", 75)]),
            *cuenta_regresiva(L, "aullido", "decidir", f"0.9 * {L}.Variable(Ritmo)", [siguiente_paso]),
        ], color="jefe"),
        GRUPO("Jefe: recibir daño", [
            E([choca("Carta", L), *activo],
              [var_o(L, "Vida", "-", "Carta.Variable(Dano)"), var_o(L, "Golpe", "=", 0.12),
               crear("Impacto", "Carta.X()", "Carta.Y()"), var_s("Hitstop", "=", 2),
               sonido_fx("golpe")],
              [E([es("atascado")], [var_o(L, "Vida", "-", "Carta.Variable(Dano) * 0.5")]),
               E([], [borrar("Carta")])]),
            NOTA("Durante la transición y la derrota las cartas rebotan: no se le puede pegar a "
                 "alguien que está hablando."),
            E([choca("Carta", L)], [crear("Chispa", "Carta.X()", "Carta.Y()"), borrar("Carta")]),
            E([C("CollisionNP", "Explosion", L, "", "", ""), si_var_o("Explosion", "Activa", "=", 1), *activo],
              [var_o(L, "Vida", "-", 35), var_o(L, "Golpe", "=", 0.2)]),
            E([si_var_o("GarraLuna", "Reflejada", "=", 1), choca("GarraLuna", L), *activo],
              [var_o(L, "Vida", "-", 40), var_o(L, "Golpe", "=", 0.25),
               crear("Impacto", "GarraLuna.X()", "GarraLuna.Y()"), var_s("Hitstop", "=", 6),
               var_s("Temblor", "=", 5), borrar("GarraLuna"), sonido_fx("golpe")]),
            E([si_var_o(L, "Golpe", ">", 0)], [var_o(L, "Golpe", "-", DT), A("ChangeColor", L, '"190;150;255"')]),
            E([si_var_o(L, "Golpe", "<=", 0)], [A("ChangeColor", L, '"255;255;255"')]),
            E([*golpeable, choca(V, L), *activo],
              [var_o(V, "Dano", "=", 10), var_o(V, "EmpujeDir", "=", f"sign({V}.X() - {L}.X() + 0.01)")],
              [E([es("embestida")], [var_o(V, "Dano", "=", 25)])]),
        ], color="jefe"),
        GRUPO("Jefe: transición de fase y derrota", [
            NOTA("A la mitad de la vida, Ambrosio aparece un instante dentro del lobo y habla. Se "
                 "limpian los ataques en el aire para que el diálogo no sea una trampa."),
            E([si_var_o(L, "Fase", "=", 1), comparar(f"{L}.Variable(Vida)", "<=", f"{L}.Variable(VidaMax) * 0.5"), *activo],
              [a("transicion"), var_o(L, "T", "=", 0), anim(L, "Transicion"),
               borrar("GarraLuna"), borrar("Onda"), borrar("Zarpazo"),
               var_s("Temblor", "=", 6), sonido_fx("transicion", 70), *iniciar_dialogo("Transicion")]),
            E([es("transicion"), si_var_s("Dialogo.Activo", "=", 0)], [var_o(L, "T", "+", DT)]),
            E([es("transicion"), si_var_o(L, "T", ">=", 1.0)],
              [var_o(L, "Fase", "=", 2), var_o(L, "Paso", "=", 0), a("decidir"), var_o(L, "T", "=", 0.6),
               texto("NombreJefe", '"Ambrosio, el Lobo"'), var_s("Temblor", "=", 5), sonido_fx("aullido", 75)]),
            E([si_var_o(L, "Vida", "<=", 0), es("derrota", True)],
              [a("derrota"), var_o(L, "T", "=", 3.4), anim(L, "Derrota"), var_s("Pelea", "=", 2),
               var_s("Bloqueado", "=", 1), borrar("GarraLuna"), borrar("Onda"), borrar("Zarpazo"),
               A("Hide", "BarraJefeFondo"), A("Hide", "BarraJefe"), A("Hide", "NombreJefe"),
               var_s("Hitstop", "=", 10), var_s("Temblor", "=", 10), sonido_fx("derrota_jefe", 80),
               texto_s("RetratoAmbrosio", '"Ambrosio"'), parar_musica()]),
            E([es("derrota")], [var_o(L, "T", "-", DT)]),
            E([es("derrota"), si_var_o(L, "T", "<=", 0), si_var_s("FinalIniciado", "=", 0)],
              [var_s("FinalIniciado", "=", 1), *iniciar_dialogo("Final", "salir")]),
        ], color="jefe"),
        GRUPO("Jefe: si Ventura cae", [
            NOTA("Morir contra el jefe reinicia la pelea entera (vida, fase y posición), justo "
                 "antes de que Ventura reaparezca. Si el jefe conservara el daño, perder no "
                 "costaría nada y la pelea dejaría de ser un examen de lo aprendido."),
            E([si_var_o(V, "Muerto", "=", 1), si_var_o(V, "TiempoMuerte", ">=", 2.0), si_var_s("Pelea", "=", 1)],
              [var_o(L, "Vida", "=", f"{L}.Variable(VidaMax)"), var_o(L, "Fase", "=", 1),
               var_o(L, "Paso", "=", 0), a("decidir"), var_o(L, "T", "=", 1.5),
               A("SetX", L, "=", 32 * CELDA), mirar, borrar("GarraLuna"), borrar("Onda"),
               borrar("Zarpazo"), texto("NombreJefe", '"Ambrosio, el Farolero"')]),
        ], color="jefe"),
        GRUPO("Jefe: orientación y barra de vida", [
            E([si_var_o(L, "Dir", "=", 1)], [voltear(L, False)]),
            E([si_var_o(L, "Dir", "=", -1)], [voltear(L, True)]),
            E([], [ancho("BarraJefe", "=", f"max(0, 236 * {L}.Variable(Vida) / {L}.Variable(VidaMax))"),
                   A("SetX", "NombreJefe", "=", "320 - NombreJefe.Width() / 2")]),
        ], color="jefe"),
    ]


# =================================================================== FINAL Y CRÉDITOS

def escena_final():
    t = PX / "titulo"
    objetos = [
        sprite(rec, "FondoFinal", [("Default", [PX / "fondos" / "arena_ciudad.png"], 1, False)], origen=(0, 0)),
        sprite(rec, "Velo", [("Default", [PX / "hud" / "Negro.png"], 1, False)], origen=(0, 0)),
        sprite(rec, "Logo", [("Default", [t / "logo.png"], 1, False)], origen=(0, 0)),
        bitmap("Epilogo", alinear="center", escala_=1.0),
        bitmap("Creditos", alinear="center", escala_=1.0),
    ]
    lw, lh = tamano(t / "logo.png")
    epilogo = [
        "Ventura no se movió de su lado hasta que amaneció.",
        "Con el sol, la tinta plateada se secó. Por ahora.",
        "En la carpa, el farol con la A grabada sigue encendido.",
        "Y cada noche, antes de salir, Ventura mira la luna una sola vez.",
    ]
    creditos = lineas(
        "UN JUEGO DE", "", "Fernando Rodríguez", "Mateo Fernández",
        "Natalia Ailén González", "Fernando Rubén Bareiro Ruiz", "", "", "CÁTEDRA",
        "Multimedia y Juegos en Web", "Lic. Fabián Marcelo Pineda",
        "Téc. Univ. Hernán Ignacio Hernández", "Prog. Juan Ignacio Carubia Grieco", "", "",
        "Tecnicatura Universitaria en Desarrollo Web", "Facultad de Ciencias de la Administración",
        "Universidad Nacional de Entre Ríos - 2026", "", "", "Hecho con GDevelop", "", "", "",
        "Gracias por jugar")
    inst = [
        instancia("FondoFinal", 0, 0, "", z=0),
        instancia("Velo", 0, 0, "", z=1, w=W, h=H),
        instancia("Logo", (W - lw) // 2, -200, "", z=2),
        instancia("Epilogo", 320, 160, "", z=3, w=560, h=40),
        instancia("Creditos", 320, H + 20, "", z=3),
        instancia("Negro", 0, 0, "Transicion", w=W, h=H),
    ]
    ev = [
        NOTA("Epílogo en cuatro frases que aparecen y se desvanecen una por una, y después los "
             "créditos suben. Enter adelanta; al terminar vuelve al título. Hay dos negros: uno "
             "fijo detrás del texto (oscurece la torre para que se lea) y el de la capa de "
             "transición, que sólo hace los fundidos de entrada y salida."),
        E([al_iniciar()], [var_s("Fundido", "=", 1), var_s("FundidoObjetivo", "=", 0),
                           tam("Negro", 640, 360), tam("Velo", 640, 360), opacidad("Velo", "=", 150),
                           texto("Creditos", creditos),
                           opacidad("Epilogo", "=", 0), opacidad("Creditos", "=", 0), musica("final", 50)]),
        E([], [var_s("Fundido", "+", "(Variable(FundidoObjetivo) - Variable(Fundido)) * min(1, 3 * TimeDelta())"),
               var_s("Tiempo", "+", DT)]),
        E([], [opacidad("Negro", "=", "Variable(Fundido) * 255")]),
        NOTA("Cada frase dura 4 s: 1 s de aparición, 2 de lectura y 1 de salida."),
        *[E([comparar("Variable(Tiempo)", ">=", 1 + 4 * i), comparar("Variable(Tiempo)", "<", 5 + 4 * i)],
            [texto("Epilogo", f'"{frase}"'),
             opacidad("Epilogo", "=", f"clamp(min(Variable(Tiempo) - {1 + 4 * i}, {5 + 4 * i} - Variable(Tiempo)) * 255, 0, 255)")])
          for i, frase in enumerate(epilogo)],
        E([comparar("Variable(Tiempo)", ">=", 1 + 4 * len(epilogo))],
          [opacidad("Epilogo", "=", 0), opacidad("Creditos", "=", 255),
           A("SetY", "Creditos", "-", f"26 * {DT}"),
           A("SetY", "Logo", "=", "Creditos.Y() - 120")]),
        E([], [A("SetX", "Epilogo", "=", "320 - Epilogo.Width() / 2"),
               A("SetX", "Creditos", "=", "320 - Creditos.Width() / 2")]),
        E([O(tecla_recien("Return"), tecla_recien("Escape"), C("HasAnyTouchStarted", ""),
             C("PosY", "Creditos", "<", "-Creditos.Height() - 20"))],
          [var_s("Saliendo", "=", 1), var_s("FundidoObjetivo", "=", 1)]),
        E([si_var_s("Saliendo", "=", 1), si_var_s("Fundido", ">", 0.97)], [cambiar_escena("Titulo")]),
    ]
    capas = [capa(""), capa("Transicion")]
    return escena("Final", capas, objetos, inst, ev,
                  {"Fundido": 1, "FundidoObjetivo": 0, "Tiempo": 0, "Saliendo": 0, "SinSonido": 0})


# =================================================================== TÍTULO

CAPITULOS = [("Prólogo: la carpa de Ambrosio", "Prologo"), ("1. Barrio del Reloj", "Nivel1"),
             ("2. Barrio de los Teatros", "Nivel2"), ("3. El Corazón de Toonaria", "Nivel3"),
             ("La cima de la torre", "ArenaJefe"), ("Volver", "")]


def escena_titulo():
    t = PX / "titulo"
    opciones = ["Jugar", "Capítulos", "Controles", "Créditos"]
    objetos = [
        sprite(rec, "FondoTitulo", [("Default", [t / "fondo.png"], 1, False)], origen=(0, 0)),
        sprite(rec, "Logo", [("Default", [t / "logo.png"], 1, False)], origen=(0, 0)),
        mosaico(rec, "NubesTitulo", PX / "fondos" / "n3_nubes_cerca.png", 960, 130),
        mosaico(rec, "BrumaTitulo", PX / "fondos" / "n3_bruma.png", 640, 48),
        bitmap("Opcion", escala_=2.0, alinear="center"),
        panel(rec, "PanelMenu", PX / "hud" / "CajaDialogo.png", 200, 114, 6),
        panel(rec, "PanelFondo", PX / "hud" / "CajaDialogo.png", 440, 280, 6),
        bitmap("PanelTexto", alinear="center"),
        bitmap("CapOpcion", alinear="center"),
        bitmap("Pie", "Tecnicatura Universitaria en Desarrollo Web - UNER - 2026", alinear="center",
               tinte="176;133;214"),
        sprite(rec, "Selector", [("Default", frames_de(PX / "proyectiles", "Carta1"), 0.1, True)],
               origen=(7, 8)),
    ]
    lw, lh = tamano(t / "logo.png")
    inst = [
        instancia("FondoTitulo", 0, 0, "", z=0),
        instancia("NubesTitulo", 0, 10, "", z=1, w=W, h=130),
        instancia("Logo", (W - lw) // 2, 112, "", z=3),
        instancia(V, 560, 344, "", z=4),
        instancia("BrumaTitulo", 0, H - 52, "", z=5, w=W, h=48),
        instancia("PanelMenu", 220, 222, "", z=5, w=200, h=114),
        *[instancia("Opcion", 320, 228 + i * 25, "", z=6, vars_={"Indice": i}) for i in range(len(opciones))],
        instancia("Selector", 240, 238, "", z=6),
        instancia("PanelFondo", 100, 40, "Panel", z=0, w=440, h=280),
        instancia("PanelTexto", 320, 60, "Panel", z=1),
        *[instancia("CapOpcion", 320, 104 + i * 26, "Panel", z=1, vars_={"Indice": i})
          for i in range(len(CAPITULOS))],
        instancia("Pie", 320, 344, "", z=6),
        instancia("Negro", 0, 0, "Transicion", w=W, h=H),
    ]
    controles = lineas("CONTROLES", "", "Mover: flechas o A / D",
                       "Saltar (doble en el aire): Espacio o W",
                       "Carta lunar: mantener X o J para cargar, soltar para tirar",
                       "Farol incendiario: C o K", "Parry: Z o L (justo antes del golpe)",
                       "Pasar diálogos: Enter", "Pausa: Esc",
                       "En celular o tablet: botones en pantalla", "", "Enter o tocar para volver")
    creditos = lineas("CRÉDITOS", "", "Fernando Rodríguez", "Mateo Fernández",
                      "Natalia Ailén González", "Fernando Rubén Bareiro Ruiz", "",
                      "Cátedra: Lic. Fabián M. Pineda", "Téc. Univ. Hernán I. Hernández",
                      "Prog. Juan Ignacio Carubia Grieco", "", "Enter o tocar para volver")

    def abrir_panel(contenido):
        return [var_s("PanelAbierto", "=", 1), texto("PanelTexto", contenido),
                A("Hide", "CapOpcion"), A("ShowLayer", "", '"Panel"')]

    cerrar = [var_s("PanelAbierto", "=", 2), A("HideLayer", "", '"Panel"')]
    n_op, n_cap = len(opciones), len(CAPITULOS)
    ev = [
        NOTA("Menú de título: cuatro opciones, arriba/abajo para elegir, Enter para confirmar. "
             "Controles, Créditos y Capítulos se muestran en una capa encima en vez de en otra "
             "escena, así el fondo animado sigue vivo detrás."),
        E([al_iniciar()],
          [var_s("Fundido", "=", 1), var_s("FundidoObjetivo", "=", 0), var_s("Seleccion", "=", 0),
           A("HideLayer", "", '"Panel"'), tam("Negro", 640, 360), anim(V, "Idle"), musica("titulo"),
           A("ActivateBehavior", V, "PlatformerObject", "no")]),
        NOTA("Los textos bitmap se ubican por su borde izquierdo: para centrarlos se resta "
             "la mitad de su ancho real (que depende del texto y de la escala)."),
        E([], [A("SetX", "Opcion", "=", "320 - Opcion.Width() / 2"),
               A("SetX", "PanelTexto", "=", "320 - PanelTexto.Width() / 2"),
               A("SetX", "CapOpcion", "=", "320 - CapOpcion.Width() / 2"),
               A("SetX", "Pie", "=", "320 - Pie.Width() / 2")]),
        E([], [var_s("Fundido", "+", "(Variable(FundidoObjetivo) - Variable(Fundido)) * min(1, 5 * TimeDelta())"),
               opacidad("Negro", "=", "Variable(Fundido) * 255"), var_s("Tiempo", "+", DT),
               A("TiledSpriteObject::XOffset", "NubesTitulo", "=", "Variable(Tiempo) * 8"),
               A("TiledSpriteObject::XOffset", "BrumaTitulo", "=", "Variable(Tiempo) * 18"),
               A("SetY", "Logo", "=", "112 + sin(Variable(Tiempo) * 1.5) * 2")]),
        PARA_CADA("Opcion", [], [], [
            *[E([si_var_o("Opcion", "Indice", "=", i)], [texto("Opcion", f'"{o}"')])
              for i, o in enumerate(opciones)],
            E([comparar("Opcion.Variable(Indice)", "=", "Variable(Seleccion)")],
              [A("BitmapText::SetTint", "Opcion", '"238;226;246"')]),
            E([comparar("Opcion.Variable(Indice)", "!=", "Variable(Seleccion)")],
              [A("BitmapText::SetTint", "Opcion", '"140;134;149"')])]),
        PARA_CADA("CapOpcion", [], [], [
            *[E([si_var_o("CapOpcion", "Indice", "=", i)], [texto("CapOpcion", f'"{nombre}"')])
              for i, (nombre, _) in enumerate(CAPITULOS)],
            E([comparar("CapOpcion.Variable(Indice)", "=", "Variable(CapSel)")],
              [A("BitmapText::SetTint", "CapOpcion", '"238;226;246"')]),
            E([comparar("CapOpcion.Variable(Indice)", "!=", "Variable(CapSel)")],
              [A("BitmapText::SetTint", "CapOpcion", '"140;134;149"')])]),
        E([si_var_s("PanelAbierto", "=", 0), si_var_s("Iniciando", "=", 0),
           O(tecla_recien("Down"), tecla_recien("s"))],
          [var_s("Seleccion", "=", f"mod(Variable(Seleccion) + 1, {n_op})"), sonido_fx("menu", 40)]),
        E([si_var_s("PanelAbierto", "=", 0), si_var_s("Iniciando", "=", 0),
           O(tecla_recien("Up"), tecla_recien("w"))],
          [var_s("Seleccion", "=", f"mod(Variable(Seleccion) + {n_op - 1}, {n_op})"),
           sonido_fx("menu", 40)]),
        NOTA("Con pantalla táctil (o mouse) tocar una opción la elige y la confirma en el mismo "
             "gesto: Confirmar hace las veces del Enter en los eventos de abajo."),
        E([], [var_s("Confirmar", "=", 0)]),
        E([si_var_s("PanelAbierto", "=", 0), si_var_s("Iniciando", "=", 0),
           C("HasAnyTouchOrMouseStarted", ""), C("SourisSurObjet", "Opcion", "", "yes", "")],
          [var_s("Seleccion", "=", "Opcion.Variable(Indice)"), var_s("Confirmar", "=", 1)]),
        E([si_var_s("PanelAbierto", "=", 3), si_var_s("Iniciando", "=", 0),
           C("HasAnyTouchOrMouseStarted", ""), C("SourisSurObjet", "CapOpcion", "", "yes", "")],
          [var_s("CapSel", "=", "CapOpcion.Variable(Indice)"), var_s("Confirmar", "=", 1)]),
        E([si_var_s("PanelAbierto", "=", 1), C("HasAnyTouchOrMouseStarted", "")],
          [var_s("PanelAbierto", "=", 2), A("HideLayer", "", '"Panel"')]),
        E([], [A("SetXY", "Selector", "=", "238 + sin(Variable(Tiempo) * 6) * 2", "=",
                 "238 + Variable(Seleccion) * 25")]),
        NOTA("Capítulos: todos disponibles desde el principio. Es una entrega para mostrar y "
             "defender, así que poder ir directo a cualquier nivel o al jefe importa más que "
             "obligar a desbloquearlos."),
        E([si_var_s("PanelAbierto", "=", 3), si_var_s("Iniciando", "=", 0),
           O(tecla_recien("Down"), tecla_recien("s"))],
          [var_s("CapSel", "=", f"mod(Variable(CapSel) + 1, {n_cap})"), sonido_fx("menu", 40)]),
        E([si_var_s("PanelAbierto", "=", 3), si_var_s("Iniciando", "=", 0),
           O(tecla_recien("Up"), tecla_recien("w"))],
          [var_s("CapSel", "=", f"mod(Variable(CapSel) + {n_cap - 1}, {n_cap})"),
           sonido_fx("menu", 40)]),
        E([si_var_s("PanelAbierto", "=", 3), si_var_s("Iniciando", "=", 0),
           O(tecla_recien("Return"), si_var_s("Confirmar", "=", 1))],
          [sonido_fx("menu_ok", 50)],
          [*[E([si_var_s("CapSel", "=", i)],
               [texto_s("Destino", f'"{escena_}"'), var_s("Iniciando", "=", 1),
                var_s("FundidoObjetivo", "=", 1)])
             for i, (_, escena_) in enumerate(CAPITULOS) if escena_],
           E([si_var_s("CapSel", "=", n_cap - 1)], cerrar)]),
        E([O(si_var_s("PanelAbierto", "=", 1), si_var_s("PanelAbierto", "=", 3)),
           si_var_s("Iniciando", "=", 0), tecla_recien("Escape")], cerrar),
        E([si_var_s("PanelAbierto", "=", 1), tecla_recien("Return")], cerrar),
        E([si_var_s("PanelAbierto", "=", 0), si_var_s("Iniciando", "=", 0),
           O(tecla_recien("Return"), si_var_s("Confirmar", "=", 1))],
          [sonido_fx("menu_ok", 50)],
          [E([si_var_s("Seleccion", "=", 0)],
             [texto_s("Destino", '"Prologo"'), var_s("Iniciando", "=", 1), var_s("FundidoObjetivo", "=", 1)]),
           E([si_var_s("Seleccion", "=", 1)],
             [var_s("PanelAbierto", "=", 3), var_s("CapSel", "=", 0),
              texto("PanelTexto", '"CAPÍTULOS"'), A("Show", "CapOpcion", ""),
              A("ShowLayer", "", '"Panel"')]),
           E([si_var_s("Seleccion", "=", 2)], abrir_panel(controles)),
           E([si_var_s("Seleccion", "=", 3)], abrir_panel(creditos))]),
        NOTA("PanelAbierto pasa por el valor 2 durante un cuadro: si no, el mismo Enter que "
             "cierra el panel volvería a abrirlo en el evento de abajo."),
        E([si_var_s("PanelAbierto", "=", 2)], [var_s("PanelAbierto", "=", 0)]),
        E([si_var_s("Iniciando", "=", 1), si_var_s("Fundido", ">", 0.97)],
          [A("Scene", "", "VariableString(Destino)", "yes")]),
    ]
    capas = [capa(""), capa("Panel"), capa("Transicion")]
    return escena("Titulo", capas, objetos, inst, ev,
                  {"Fundido": 1, "FundidoObjetivo": 0, "Seleccion": 0, "PanelAbierto": 0,
                   "Iniciando": 0, "Tiempo": 0, "SinSonido": 0, "CapSel": 0, "Destino": "Prologo",
                   "Confirmar": 0})


# =================================================================== PROYECTO

def propiedades():
    return {
        "adaptGameResolutionAtRuntime": False, "antialiasingMode": "none",
        "antialisingEnabledOnMobile": False, "folderProject": False, "orientation": "landscape",
        "packageName": "ar.edu.uner.toonaria", "pixelsRounding": True,
        "projectUuid": "6f1d1c52-2a3c-4b8e-9b0e-7d3c1f2a9a10", "scaleMode": "nearest",
        "sizeOnStartupMode": "", "templateSlug": "", "useDeprecatedZeroAsDefaultStringVariable": False,
        "version": "1.0.0", "name": "Toonaria",
        "description": "Plataformero de acción en pixel art: una ciudad de tinta donde la luna llena "
                       "repinta a sus habitantes. Trabajo integrador - Multimedia y Juegos en Web, UNER.",
        "author": "Rodríguez, Fernández, González, Bareiro Ruiz", "windowWidth": W,
        "windowHeight": H, "latestCompilationDirectory": "", "maxFPS": 60, "minFPS": 20,
        "verticalSync": True, "platformSpecificAssets": {},
        "loadingScreen": {"backgroundColor": 1183764, "backgroundFadeInDuration": 0.2,
                          "backgroundImageResourceName": "", "gdevelopLogoStyle": "light",
                          "logoAndProgressFadeInDuration": 0.2, "logoAndProgressLogoFadeInDelay": 0.2,
                          "minDuration": 1, "progressBarColor": 11568598, "progressBarHeight": 6,
                          "progressBarMaxWidth": 200, "progressBarMinWidth": 40,
                          "progressBarWidthPercent": 30, "showGDevelopSplash": True,
                          "showProgressBar": True},
        "watermark": {"placement": "bottom-left", "showWatermark": True},
        "authorIds": [], "authorUsernames": [], "categories": ["platformer"],
        "playableDevices": ["keyboard", "mobile"], "extensionProperties": [],
        "platforms": [{"name": "GDevelop JS platform"}], "currentPlatform": "GDevelop JS platform",
    }


def main():
    globales = objetos_globales()
    c = CELDA
    escenas = [
        escena_titulo(),
        escena_nivel("Prologo", PROLOGO, "prologo", DIALOGOS_PROLOGO, "Nivel1",
                     [(3 * c, "Inicio", ""), (23 * c, "Doble", ""), (31 * c, "Cartas", ""),
                      (43 * c, "Farol", ""), (56 * c, "Parry", ""), (66 * c, "Final", "salir")],
                     prefijo_tiles="carpa", interior=True, objetos_extra=objetos_prologo(),
                     inst_extra=[instancia("Ambrosio", 9 * c + 8, 18 * c, "", z=9),
                                 instancia("Barrera", 61 * c, -400, "", w=16, h=H + 800)],
                     enlaces_extra=["Prologo"],
                     vars_extra={"Movido": 0, "Leccion": 0, "TiroT": 0, "GestoT": 0},
                     tema="carpa"),
        escena_nivel("Nivel1", NIVEL1, "n1", DIALOGOS_N1, "Nivel2",
                     [(13 * c, "Inicio", ""), (228 * c, "Final", "salir")],
                     tema="barrios", resultados=True),
        escena_nivel("Nivel2", NIVEL2, "n2", DIALOGOS_N2, "Nivel3",
                     [(10 * c, "Inicio", ""), (240 * c, "Final", "")],
                     objetos_extra=[sprite(rec, "ActorEco",
                                           [("Idle", frames_de(PX / "actor", "Idle"), 0.16, True)],
                                           origen=(48, 62))],
                     inst_extra=[instancia("ActorEco", 245 * c + 8, 18 * c, "", z=9)],
                     eventos_extra=[E([al_iniciar()], [voltear("ActorEco", True)])],
                     tema="barrios", resultados=True),
        escena_nivel("Nivel3", NIVEL3, "n3", DIALOGOS_N3, "ArenaJefe",
                     [(10 * c, "Inicio", ""), (262 * c, "Final", "salir")],
                     tema="corazon", resultados=True),
        escena_nivel("ArenaJefe", ARENA, "arena", DIALOGOS_ARENA, "Final",
                     [(5 * c, "Encuentro", "")],
                     prefijo_tiles="torre", interior=True, objetos_extra=objetos_jefe(),
                     inst_extra=[instancia("Lobo", 32 * c, 18 * c, "", z=8),
                                 instancia("BarraJefeFondo", 200, 340, "HUD"),
                                 instancia("BarraJefe", 202, 342, "HUD", w=236, h=6),
                                 instancia("NombreJefe", 320, 326, "HUD")],
                     enlaces_extra=["Jefe"],
                     vars_extra={"Pelea": 0, "Encuentro": 0, "FinalIniciado": 0,
                                 "RetratoAmbrosio": "Lobo"}),
        escena_final(),
    ]
    externos = [externo("Tactil", "Nivel1", eventos_tactil()),
                externo("Nivel", "Nivel1", eventos_nivel()),
                externo("Jugador", "Nivel1", eventos_jugador()),
                externo("Combate", "Nivel1", eventos_combate()),
                externo("Enemigos", "Nivel1", eventos_enemigos()),
                externo("Obstaculos", "Nivel1", eventos_obstaculos()),
                externo("Dialogo", "Nivel1", eventos_dialogo()),
                externo("Camara", "Nivel1", eventos_camara()),
                externo("HUD", "Nivel1", eventos_hud()),
                externo("Prologo", "Prologo", eventos_prologo()),
                externo("Jefe", "ArenaJefe", eventos_jefe())]
    proyecto = {
        "firstLayout": "Titulo",
        "gdVersion": {"build": 269, "major": 5, "minor": 6, "revision": 0},
        "properties": propiedades(),
        "resources": {"resources": rec.lista, "resourceFolders": []},
        "objects": globales,
        "objectsFolderStructure": {"folderName": "__ROOT",
                                   "children": [{"objectName": o["name"]} for o in globales]},
        "objectsGroups": GRUPOS_GLOBALES,
        "variables": [],
        "layouts": escenas,
        "externalEvents": externos,
        "eventsFunctionsExtensions": [],
        "externalLayouts": [],
    }
    import json
    destino = JUEGO / "game.json"
    destino.write_text(json.dumps(proyecto, ensure_ascii=False, indent=2), encoding="utf-8")
    print("game.json:", len(escenas), "escenas,", len(globales), "objetos globales,",
          len(rec.lista), "recursos")


if __name__ == "__main__":
    main()
