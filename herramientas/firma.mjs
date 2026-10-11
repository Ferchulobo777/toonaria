// Muestra la firma (parámetros) de una o más instrucciones según los metadatos del motor.
// Uso: node herramientas/firma.mjs c:PlatformBehavior::IsOnFloor a:Create ...
//      (prefijo c: condición, a: acción, e: expresión numérica, s: expresión de texto)

import { gd } from "gdcore-tools";

const plataforma = gd.JsPlatform.get();
const MP = gd.MetadataProvider;

for (const arg of process.argv.slice(2)) {
  const [clase, tipo] = arg.includes(":") && arg[1] === ":" ? [arg[0], arg.slice(2)] : ["a", arg];
  let meta;
  if (clase === "c") meta = MP.getConditionMetadata(plataforma, tipo);
  else if (clase === "a") meta = MP.getActionMetadata(plataforma, tipo);
  if (!meta || MP.isBadInstructionMetadata(meta)) {
    console.log(`${arg}: NO EXISTE`);
    continue;
  }
  const params = [];
  for (let i = 0; i < meta.getParametersCount(); i++) {
    const p = meta.getParameter(i);
    const codeOnly = p.isCodeOnly() ? "*" : "";
    params.push(`${i}:${p.getType()}${codeOnly}${p.getExtraInfo() ? "<" + p.getExtraInfo() + ">" : ""}`);
  }
  console.log(`${arg}${meta.isHidden() ? " (oculta/obsoleta)" : ""}\n    ${params.join(" | ")}`);
}
