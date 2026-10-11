// Valida los event sheets de game.json contra los metadatos reales del motor (libGD).
//
// El exportador de GDevelop descarta en silencio cualquier condición o acción cuyo tipo no
// reconoce: el juego compila y corre, pero ese evento nunca hace nada. Este script recorre
// todas las escenas y eventos externos y reporta, para cada instrucción, si el tipo existe y
// si la cantidad de parámetros coincide con la que declara el motor. También controla que el
// objeto de cada instrucción sea del tipo que la instrucción pide (por ejemplo, teñir un texto
// bitmap con la acción de color de los Sprite no da error al exportar pero no hace nada).
//
// Uso: node herramientas/validar_eventos.mjs juego/game.json

import { readFileSync } from "node:fs";
import { gd } from "gdcore-tools";

const ruta = process.argv[2] ?? "juego/game.json";
const proyecto = JSON.parse(readFileSync(ruta, "utf8"));
const plataforma = gd.JsPlatform.get();
const MP = gd.MetadataProvider;

const errores = [];
let revisadas = 0;

function metadatos(tipo, esCondicion) {
  const meta = esCondicion
    ? MP.getConditionMetadata(plataforma, tipo)
    : MP.getActionMetadata(plataforma, tipo);
  return MP.isBadInstructionMetadata(meta) ? null : meta;
}

// Tipo de cada objeto (globales + los de la escena) y miembros de cada grupo.
const globales = Object.fromEntries((proyecto.objects ?? []).map((o) => [o.name, o.type]));
const gruposGlobales = Object.fromEntries((proyecto.objectsGroups ?? []).map((g) => [g.name, g.objects.map((o) => o.name)]));
let tipos = globales;
let grupos = gruposGlobales;
function usarEscena(nombre) {
  const escena = proyecto.layouts.find((l) => l.name === nombre);
  tipos = { ...globales, ...Object.fromEntries((escena?.objects ?? []).map((o) => [o.name, o.type])) };
  grupos = { ...gruposGlobales, ...Object.fromEntries((escena?.objectsGroups ?? []).map((g) => [g.name, g.objects.map((o) => o.name)])) };
}

function revisarTipoObjeto(meta, inst, clase, lugar) {
  const params = inst.parameters ?? [];
  for (let i = 0; i < Math.min(params.length, meta.getParametersCount()); i++) {
    const pm = meta.getParameter(i);
    if (!gd.ParameterMetadata.isObject(pm.getType())) continue;
    const pedido = pm.getExtraInfo();
    if (!pedido) continue;
    const nombre = params[i];
    const miembros = grupos[nombre] ?? [nombre];
    for (const m of miembros) {
      const real = tipos[m];
      if (real && real !== pedido) {
        errores.push(`${lugar}: ${clase} "${inst.type.value}" pide un objeto ${pedido} y "${m}" es ${real}`);
      }
    }
  }
}

function revisarInstruccion(inst, esCondicion, lugar) {
  revisadas++;
  const tipo = inst.type.value;
  const meta = metadatos(tipo, esCondicion);
  const clase = esCondicion ? "condición" : "acción";
  if (!meta) {
    errores.push(`${lugar}: ${clase} desconocida "${tipo}"`);
    return;
  }
  const esperados = meta.getParametersCount();
  // Los parámetros "codeOnly" (por ejemplo el contexto de escena) también ocupan lugar en el
  // arreglo del JSON, así que la cantidad tiene que coincidir con el total declarado.
  revisarTipoObjeto(meta, inst, clase, lugar);
  const recibidos = (inst.parameters ?? []).length;
  if (recibidos !== esperados) {
    errores.push(`${lugar}: ${clase} "${tipo}" espera ${esperados} parámetros y tiene ${recibidos}`);
  }
  for (const sub of inst.subInstructions ?? []) revisarInstruccion(sub, esCondicion, lugar);
}

function recorrer(eventos, lugar) {
  eventos.forEach((ev, i) => {
    const aqui = `${lugar} #${i + 1}`;
    for (const c of ev.conditions ?? []) revisarInstruccion(c, true, aqui);
    for (const a of ev.actions ?? []) revisarInstruccion(a, false, aqui);
    for (const c of ev.whileConditions ?? []) revisarInstruccion(c, true, aqui);
    if (ev.events) recorrer(ev.events, aqui);
  });
}

for (const escena of proyecto.layouts) { usarEscena(escena.name); recorrer(escena.events, `[${escena.name}]`); }
for (const ext of proyecto.externalEvents ?? []) {
  usarEscena(ext.associatedLayout);
  recorrer(ext.events, `[externo ${ext.name}]`);
}

console.log(`Instrucciones revisadas: ${revisadas}`);
if (errores.length) {
  console.log(`Problemas: ${errores.length}`);
  for (const e of errores) console.log("  - " + e);
  process.exitCode = 1;
} else {
  console.log("Sin problemas: todas las instrucciones existen y tienen los parámetros correctos.");
}
