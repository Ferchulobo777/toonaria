// Valida las fórmulas (expresiones) de todos los eventos con el analizador real del motor.
//
// Complementa a validar_eventos.mjs: aquel controla que cada condición/acción exista y tenga
// la cantidad correcta de parámetros; este controla que lo que va DENTRO de cada parámetro
// numérico o de texto sea una expresión válida para esa escena (objetos, variables y funciones
// que existen, paréntesis balanceados, tipos correctos). Un error acá el editor lo marca en
// rojo, pero el exportador lo convierte en 0 o "" sin avisar.
//
// Uso: node herramientas/validar_expresiones.mjs juego/game.json

import { readFileSync } from "node:fs";
import { gd, loadProject } from "gdcore-tools";

const ruta = process.argv[2] ?? "juego/game.json";
const json = JSON.parse(readFileSync(ruta, "utf8"));
const proyecto = await loadProject(ruta);
const plataforma = gd.JsPlatform.get();
const MP = gd.MetadataProvider;
const parser = new gd.ExpressionParser2();

const errores = [];
let revisadas = 0;

function contenedores(nombreEscena) {
  const escena = proyecto.getLayout(nombreEscena);
  return gd.ProjectScopedContainers.makeNewProjectScopedContainersForProjectAndLayout(
    proyecto, escena);
}

function revisarInstruccion(inst, esCondicion, lugar, psc) {
  const meta = esCondicion
    ? MP.getConditionMetadata(plataforma, inst.type.value)
    : MP.getActionMetadata(plataforma, inst.type.value);
  if (MP.isBadInstructionMetadata(meta)) return;
  const params = inst.parameters ?? [];
  for (let i = 0; i < meta.getParametersCount() && i < params.length; i++) {
    const p = meta.getParameter(i);
    const tipo = p.getType();
    let clase = null;
    if (gd.ParameterMetadata.isExpression("number", tipo)) clase = "number";
    else if (gd.ParameterMetadata.isExpression("string", tipo)) clase = "string";
    if (!clase || p.isCodeOnly()) continue;
    const texto = params[i];
    if (texto === "" && p.isOptional()) continue;
    revisadas++;
    const nodo = parser.parseExpression(texto).get();
    const validador = new gd.ExpressionValidator(plataforma, psc, clase, p.getExtraInfo());
    nodo.visit(validador);
    const diag = validador.getAllErrors();
    for (let k = 0; k < diag.size(); k++) {
      errores.push(`${lugar}: ${inst.type.value} parámetro ${i} «${texto}»: ${diag.at(k).getMessage()}`);
    }
    validador.delete();
  }
  for (const sub of inst.subInstructions ?? []) revisarInstruccion(sub, esCondicion, lugar, psc);
}

function recorrer(eventos, lugar, psc) {
  eventos.forEach((ev, i) => {
    const aqui = `${lugar} #${i + 1}`;
    for (const c of ev.conditions ?? []) revisarInstruccion(c, true, aqui, psc);
    for (const a of ev.actions ?? []) revisarInstruccion(a, false, aqui, psc);
    if (ev.events) recorrer(ev.events, aqui, psc);
  });
}

for (const escena of json.layouts) recorrer(escena.events, `[${escena.name}]`, contenedores(escena.name));
for (const ext of json.externalEvents ?? []) {
  // Cada evento externo se valida en todas las escenas que lo enlazan.
  const usan = json.layouts.filter((l) => JSON.stringify(l.events).includes(`"target":"${ext.name}"`)
    || JSON.stringify(l.events).includes(`"target": "${ext.name}"`));
  const escenas = usan.length ? usan.map((l) => l.name) : [ext.associatedLayout];
  for (const nombre of escenas) recorrer(ext.events, `[externo ${ext.name} en ${nombre}]`, contenedores(nombre));
}

console.log(`Expresiones revisadas: ${revisadas}`);
if (errores.length) {
  const unicos = [...new Set(errores)];
  console.log(`Problemas: ${unicos.length}`);
  for (const e of unicos.slice(0, 200)) console.log("  - " + e);
  process.exitCode = 1;
} else {
  console.log("Sin problemas: todas las expresiones son válidas en su escena.");
}
