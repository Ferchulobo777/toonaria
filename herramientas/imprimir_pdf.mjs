// Imprime una página HTML local a PDF A4 con número de página (usado para el GDD).
//
// Uso: node herramientas/imprimir_pdf.mjs <pagina.html> <salida.pdf>
// Requiere puppeteer (`npm install --no-save puppeteer`) o PUPPETEER_PATH apuntando a uno.

import { createRequire } from "node:module";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const puppeteer = require(process.env.PUPPETEER_PATH ? resolve(process.env.PUPPETEER_PATH) : "puppeteer");

const [html, pdf] = process.argv.slice(2);
const navegador = await puppeteer.launch({ headless: true });
const pagina = await navegador.newPage();
await pagina.goto(pathToFileURL(resolve(html)).href, { waitUntil: "load" });
await pagina.pdf({
  path: pdf, format: "A4", printBackground: true, displayHeaderFooter: true,
  headerTemplate: "<span></span>",
  footerTemplate: `<div style="width:100%;font-size:8px;color:#8C8695;padding:0 16mm;
    display:flex;justify-content:space-between;font-family:Segoe UI,Arial">
    <span>Toonaria — Game Design Document</span>
    <span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
  margin: { top: "18mm", bottom: "18mm", left: "16mm", right: "16mm" },
});
await navegador.close();
console.log("pdf", pdf);
