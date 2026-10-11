// Prueba de juego automatizada: carga la exportación web en Chromium headless, aprieta teclas
// reales (con duración) y registra el estado interno del juego y capturas de pantalla.
//
// Sirve para verificar mecánicas con teclado de verdad (salto, doble salto, carga de cartas,
// daño, pozos, checkpoints) sin depender de que alguien juegue a mano cada vez que algo cambia.
//
// Uso: node herramientas/probar_juego.mjs <carpeta_export> <escenario.json> <carpeta_salida>
// Escenario: lista de pasos, por ejemplo
//   [{"esperar": 1500}, {"tecla": "Enter"}, {"mantener": "ArrowRight", "ms": 800},
//    {"estado": "tras caminar"}, {"captura": "nivel1"}, {"escena": "Nivel1"}]

import { createServer } from "node:http";
import { readFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { extname, join, resolve } from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
// Puppeteer no es dependencia del proyecto (descarga un Chromium de ~170 MB): se instala
// aparte con `npm install --no-save puppeteer`, o se indica dónde está con PUPPETEER_PATH.
const puppeteer = require(process.env.PUPPETEER_PATH ? resolve(process.env.PUPPETEER_PATH) : "puppeteer");

const [carpeta, archivoEscenario, salida] = process.argv.slice(2);
const pasos = JSON.parse(readFileSync(archivoEscenario, "utf8"));
mkdirSync(salida, { recursive: true });

const tipos = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json",
  ".png": "image/png", ".wav": "audio/wav", ".mp3": "audio/mpeg", ".ogg": "audio/ogg",
  ".fnt": "text/plain", ".css": "text/css" };
const servidor = createServer((req, res) => {
  let ruta = decodeURIComponent(req.url.split("?")[0]);
  if (ruta === "/") ruta = "/index.html";
  const archivo = join(carpeta, ruta);
  if (!existsSync(archivo)) { res.writeHead(404); res.end(); return; }
  let cuerpo = readFileSync(archivo);
  if (ruta === "/index.html") {
    // Se expone la instancia del juego para poder leer su estado desde la prueba.
    cuerpo = cuerpo.toString().replace("var game = new gdjs.RuntimeGame(gdjs.projectData, {});",
      "var game = new gdjs.RuntimeGame(gdjs.projectData, {}); window.__juego = game;");
  }
  res.writeHead(200, { "Content-Type": tipos[extname(archivo)] ?? "application/octet-stream" });
  res.end(cuerpo);
});
await new Promise((r) => servidor.listen(0, "127.0.0.1", r));
const puerto = servidor.address().port;

const navegador = await puppeteer.launch({ headless: true, args: ["--autoplay-policy=no-user-gesture-required"] });
const pagina = await navegador.newPage();
await pagina.setViewport({ width: 1280, height: 720 });
const consola = [];
pagina.on("console", (m) => { if (m.type() === "error" || m.type() === "warn") consola.push(`[${m.type()}] ${m.text()}`); });
pagina.on("pageerror", (e) => consola.push(`[pageerror] ${e.message}`));
await pagina.goto(`http://127.0.0.1:${puerto}/`, { waitUntil: "load" });
await pagina.waitForFunction(() => window.__juego && window.__juego.getSceneStack().getCurrentScene(), { timeout: 30000 });
await pagina.click("canvas").catch(() => {});

const estado = () => pagina.evaluate(() => {
  const s = window.__juego.getSceneStack().getCurrentScene();
  const num = (vs, n) => (vs.has(n) ? Math.round(vs.get(n).getAsNumber() * 100) / 100 : null);
  const v = s.getObjects("Ventura")[0];
  const r = { escena: s.getName() };
  if (v) {
    const vv = v.getVariables();
    const b = v.getBehavior("PlatformerObject");
    r.ventura = { x: Math.round(v.getX()), y: Math.round(v.getY()), anim: v.getAnimationName(),
      vida: num(vv, "Vida"), mana: num(vv, "Mana"), carga: num(vv, "Carga"),
      enPiso: b ? b.isOnFloor() : null, saltando: b ? b.isJumping() : null,
      cayendo: b ? b.isFalling() : null, opacidad: v.getOpacity() };
  }
  const sv = s.getVariables();
  r.escenaVars = {};
  for (const n of ["CheckX", "CamX", "Fundido", "Bloqueado", "Saliendo", "Pausa", "Tiempo"]) r.escenaVars[n] = num(sv, n);
  if (sv.has("Dialogo")) r.dialogo = { activo: sv.get("Dialogo").getChild("Activo").getAsNumber(), indice: sv.get("Dialogo").getChild("Indice").getAsNumber() };
  r.cantidades = {};
  for (const n of ["Repintado", "Carta", "FarolBomba", "Explosion", "Te", "Luna", "Engranaje", "Tinta"]) r.cantidades[n] = s.getObjects(n) ? s.getObjects(n).length : 0;
  const tab = s.getObjects("Tablon");
  if (tab && tab.length) r.tablones = tab.slice(0, 3).map((e) => ({ x: Math.round(e.getX()), y: Math.round(e.getY()), estado: e.getVariables().get("Estado").getAsNumber(), activo: e.behaviorActivated ? e.behaviorActivated("Platform") : null, anim: e.getAnimationName() }));
  const rep = s.getObjects("Repintado");
  if (rep && rep.length) r.repintados = rep.slice(0, 3).map((e) => ({ x: Math.round(e.getX()), estado: e.getVariables().get("Estado").getAsString(), vida: e.getVariables().get("Vida").getAsNumber() }));
  return r;
});

const registro = [];
let cuadroGif = 0;
let cdp = null;
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
for (const p of pasos) {
  if (p.esperar) await dormir(p.esperar);
  if (p.tecla) { await pagina.keyboard.press(p.tecla, { delay: 60 }); }
  if (p.mantener) {
    const teclas = Array.isArray(p.mantener) ? p.mantener : [p.mantener];
    for (const t of teclas) await pagina.keyboard.down(t);
    await dormir(p.ms ?? 300);
    for (const t of teclas.reverse()) await pagina.keyboard.up(t);
  }
  if (p.bajar) await pagina.keyboard.down(p.bajar);
  if (p.soltar) await pagina.keyboard.up(p.soltar);
  if (p.irA) {
    await pagina.evaluate((n) => window.__juego.getSceneStack().replace(n, true), p.irA);
    await dormir(800);
  }
  if (p.teletransportar) {
    await pagina.evaluate((xy) => { const v = window.__juego.getSceneStack().getCurrentScene().getObjects("Ventura")[0]; v.setX(xy[0]); v.setY(xy[1]); }, p.teletransportar);
  }
  if (p.cuadros) {
    // Graba N cuadros seguidos (requestAnimationFrame) para ver trayectorias con detalle.
    const cuadros = await pagina.evaluate((n) => new Promise((res) => {
      const out = [];
      const paso = () => {
        const s = window.__juego.getSceneStack().getCurrentScene();
        const v = s.getObjects("Ventura")[0];
        const b = v.getBehavior("PlatformerObject");
        const extra = {};
        for (const nombre of ["Toldo", "Tablon"]) {
          const o = s.getObjects(nombre);
          if (o && o.length) extra[nombre] = o.some((x) => gdjs.RuntimeObject.collisionTest(v, x, false));
        }
        out.push({ y: Math.round(v.getY() * 10) / 10, anim: v.getAnimationName(), piso: b.isOnFloor(),
          cae: b.isFalling(), salta: b.isJumping(), vc: Math.round(b.getCurrentFallSpeed()),
          vs: Math.round(b.getCurrentJumpSpeed()), ...extra });
        if (out.length < n) requestAnimationFrame(paso); else res(out);
      };
      requestAnimationFrame(paso);
    }), p.cuadros);
    registro.push({ paso: "cuadros", cuadros });
  }
  if (p.estado) registro.push({ paso: p.estado, ...(await estado()) });
  if (p.captura) await pagina.screenshot({ path: join(salida, `${p.captura}.png`) });
  if (p.grabarInicio) {
    // Transmisión de cuadros del navegador (screencast): sigue grabando mientras corren los
    // pasos siguientes, hasta "grabarFin". Sirve para armar un GIF fluido del recorrido.
    cdp = await pagina.createCDPSession();
    cdp.on("Page.screencastFrame", async (f) => {
      writeFileSync(join(salida, `g_${String(cuadroGif++).padStart(4, "0")}.jpg`), Buffer.from(f.data, "base64"));
      await cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {});
    });
    await cdp.send("Page.startScreencast", { format: "jpeg", quality: 80, maxWidth: 640, maxHeight: 360, everyNthFrame: 2 });
  }
  if (p.grabarFin && cdp) await cdp.send("Page.stopScreencast");
  if (p.explorar) registro.push({ paso: "explorar", ...(await explorar(p.explorar)) });
  // JS arbitrario en la página, con `s` = escena actual (para forzar situaciones de prueba).
  if (p.js) registro.push({ paso: "js", resultado: await pagina.evaluate(
    new Function(`const s = window.__juego.getSceneStack().getCurrentScene(); return (${p.js});`)) });
  // Muestreo de un objeto: registra sus variables cada 50 ms y guarda sólo los cambios.
  if (p.seguir) {
    const { objeto, vars, ms, teclas } = p.seguir;
    const cambios = [];
    let anterior = "";
    const t0 = Date.now();
    while (Date.now() - t0 < ms) {
      if (teclas) for (const k of teclas) await pagina.keyboard.press(k, { delay: 20 });
      const fila = await pagina.evaluate((o, vs) => {
        const s = window.__juego.getSceneStack().getCurrentScene();
        const ob = (s.getObjects(o) || [])[0];
        if (!ob) return null;
        const r = {};
        for (const v of vs) { const x = ob.getVariables().get(v); r[v] = x.getType() === "string" ? x.getAsString() : Math.round(x.getAsNumber() * 10) / 10; }
        r.anim = ob.getAnimationName(); r.x = Math.round(ob.getX());
        r.garras = (s.getObjects("GarraLuna") || []).length; r.ondas = (s.getObjects("OndaLuna") || []).length;
        r.dialogo = s.getVariables().get("Dialogo").getChild("Activo").getAsNumber();
        return r;
      }, objeto, vars);
      const clave = JSON.stringify({ ...fila, x: undefined });
      if (fila && clave !== anterior) { cambios.push({ t: Date.now() - t0, ...fila }); anterior = clave; }
      await dormir(50);
    }
    registro.push({ paso: "seguir", cambios });
  }
}

// Recorrido automático: avanza a la derecha con teclas reales, salta si se traba contra algo
// o si adelante no hay piso, usa el doble salto si en el aire sigue sin haber dónde caer y
// pasa los diálogos. No busca jugar bien: sirve para comprobar que el nivel se puede cruzar
// (que no hay paredes imposibles ni pozos sin salida) y para medir hasta dónde se llega.
async function explorar(o) {
  const hastaX = o.hastaX ?? 1e9, limite = Date.now() + (o.ms ?? 60000);
  const escenaInicial = await pagina.evaluate(() => window.__juego.getSceneStack().getCurrentScene().getName());
  let maxX = 0, trabado = 0, saltos = 0, caidas = 0, dialogos = 0, ultimoX = null, dobleUsado = false;
  let parries = 0;
  let derecha = false;
  const leer = () => pagina.evaluate((inv) => {
    const s = window.__juego.getSceneStack().getCurrentScene();
    const v = s.getObjects("Ventura")[0];
    if (!v) return { escena: s.getName() };
    const vv = v.getVariables();
    if (inv) { vv.get("Invulnerable").setNumber(5); vv.get("Vida").setNumber(100); }
    const b = v.getBehavior("PlatformerObject");
    const sv = s.getVariables();
    const x = v.getX(), y = v.getY();
    // ¿Hay algo donde apoyarse un poco más adelante (a la altura de los pies o hasta 60 px abajo)?
    let pisoAdelante = false;
    for (const n of ["Suelo", "Cornisa", "Tablon", "Barril", "Andamio", "NubeTinta"]) {
      for (const p of s.getObjects(n) || []) {
        const a = p.getAABB();
        if (a.min[0] <= x + 26 && a.max[0] >= x + 14 && a.min[1] >= y - 6 && a.min[1] <= y + 60) pisoAdelante = true;
      }
    }
    let proyCerca = false;
    for (const n of ["Mascara", "GarraLuna"]) {
      for (const p of s.getObjects(n) || []) {
        if (p.getVariables().get("Reflejada").getAsNumber() === 0 && Math.abs(p.getX() - x) < 38 &&
            Math.abs(p.getY() - (y - 24)) < 30) proyCerca = true;
      }
    }
    return { escena: s.getName(), x, y, enPiso: b.isOnFloor(), cayendo: b.isFalling(), proyCerca,
      dialogo: sv.has("Dialogo") ? sv.get("Dialogo").getChild("Activo").getAsNumber() : 0,
      bloqueado: sv.has("Bloqueado") ? sv.get("Bloqueado").getAsNumber() : 0, pisoAdelante };
  }, !!o.invulnerable);
  while (Date.now() < limite) {
    const e = await leer();
    if (e.escena !== escenaInicial) { if (derecha) await pagina.keyboard.up("ArrowRight"); return { llegoA: e.escena, maxX: Math.round(maxX), saltos, caidas, dialogos, parries }; }
    if (e.x === undefined) { await dormir(100); continue; }
    maxX = Math.max(maxX, e.x);
    if (e.x >= hastaX) break;
    if (e.dialogo === 1) {
      if (derecha) { await pagina.keyboard.up("ArrowRight"); derecha = false; }
      await pagina.keyboard.press("Enter", { delay: 30 }); dialogos++; await dormir(120); continue;
    }
    if (o.parry && e.proyCerca) { await pagina.keyboard.press("z", { delay: 30 }); parries++; }
    if (!derecha) { await pagina.keyboard.down("ArrowRight"); derecha = true; }
    if (o.atacar && Math.random() < 0.15) await pagina.keyboard.press("x", { delay: 20 });
    if (ultimoX !== null && e.x < ultimoX - 120) caidas++;
    trabado = ultimoX !== null && Math.abs(e.x - ultimoX) < 0.5 ? trabado + 1 : 0;
    ultimoX = e.x;
    if (e.enPiso) dobleUsado = false;
    if (e.enPiso && (trabado >= 3 || !e.pisoAdelante)) {
      await pagina.keyboard.down("Space"); await dormir(300); await pagina.keyboard.up("Space");
      saltos++; trabado = 0; continue;
    }
    if (!e.enPiso && e.cayendo && !dobleUsado && (!e.pisoAdelante || trabado >= 2)) {
      await pagina.keyboard.down("Space"); await dormir(260); await pagina.keyboard.up("Space");
      dobleUsado = true; saltos++; continue;
    }
    await dormir(60);
  }
  if (derecha) await pagina.keyboard.up("ArrowRight");
  const fin = await leer();
  return { llegoA: fin.escena, maxX: Math.round(maxX), x: Math.round(fin.x ?? 0), saltos, caidas, dialogos, parries };
}
writeFileSync(join(salida, "registro.json"), JSON.stringify({ registro, consola }, null, 2));
console.log(JSON.stringify({ registro, consola: consola.slice(0, 20) }, null, 1));
await navegador.close();
servidor.close();
