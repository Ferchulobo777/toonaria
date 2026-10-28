"""Convierte diseno/GDD.md en una página HTML lista para imprimir a PDF (portada, índice y estilos).

El GDD se escribe y se versiona en Markdown; la cátedra lo pide en .doc o .pdf. Generar el PDF
desde el mismo archivo evita tener dos versiones del documento que se desincronicen.

Uso: python herramientas/gdd_html.py <salida.html>
     node herramientas/imprimir_pdf.mjs <salida.html> <GDD.pdf>
"""

import re
import sys
from datetime import date
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parents[1]

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; font-size: 10.2pt;
       line-height: 1.5; color: #1d1a22; }
h1, h2, h3 { color: #46276E; line-height: 1.25; }
h1 { font-size: 22pt; margin: 0 0 6pt; }
h2 { font-size: 15pt; margin: 20pt 0 6pt; padding-bottom: 3pt; border-bottom: 1.5pt solid #B085D6;
     break-after: avoid; }
h3 { font-size: 12pt; margin: 14pt 0 4pt; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 9.2pt;
        break-inside: avoid; }
th { background: #46276E; color: #fff; text-align: left; padding: 4pt 6pt; }
td { border-bottom: 0.6pt solid #d9d2e2; padding: 3.5pt 6pt; vertical-align: top; }
tr:nth-child(even) td { background: #f6f2fa; }
code { font-family: Consolas, "Courier New", monospace; font-size: 8.8pt; background: #f1ecf6;
       padding: 0 2pt; border-radius: 2pt; }
pre { background: #1d1a22; color: #eee2f6; padding: 8pt; border-radius: 4pt; font-size: 8pt;
      overflow: hidden; break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; }
a { color: #6B3FA0; text-decoration: none; }
hr { border: none; border-top: 0.6pt solid #d9d2e2; margin: 14pt 0; }
.portada { height: 255mm; display: flex; flex-direction: column; justify-content: center;
           align-items: center; text-align: center; break-after: page; }
.portada img.logo { width: 120mm; image-rendering: pixelated; }
.portada img.captura { width: 150mm; margin: 12mm 0 8mm; border-radius: 3pt;
                       image-rendering: pixelated; box-shadow: 0 2pt 8pt rgba(0,0,0,.25); }
.portada .tipo { font-size: 16pt; color: #6B3FA0; letter-spacing: 2pt; text-transform: uppercase; }
.portada .datos { font-size: 10.5pt; color: #3a3541; margin-top: 4mm; }
.indice { break-after: page; }
.indice ol { columns: 2; column-gap: 10mm; font-size: 9.5pt; padding-left: 14pt; }
.indice li { break-inside: avoid; }
"""


def slug(texto):
    t = re.sub(r"[^\w\s-]", "", texto.lower(), flags=re.UNICODE)
    return re.sub(r"\s+", "-", t).strip("-")


def main():
    salida = Path(sys.argv[1]).resolve()
    md = (RAIZ / "diseno" / "GDD.md").read_text(encoding="utf8")
    # El título y la presentación del .md se reemplazan por la portada.
    cuerpo_md = md.split("\n---\n", 1)[1] if "\n---\n" in md else md
    html = markdown.markdown(cuerpo_md, extensions=["tables", "fenced_code", "sane_lists"])
    titulos = re.findall(r"<h2>(.*?)</h2>", html)
    for t in titulos:
        html = html.replace(f"<h2>{t}</h2>", f'<h2 id="{slug(t)}">{t}</h2>', 1)
    indice = "".join(f'<li><a href="#{slug(t)}">{t}</a></li>' for t in titulos)
    logo = (RAIZ / "juego" / "assets" / "pixel" / "titulo" / "logo.png").as_uri()
    captura = (RAIZ / "diseno" / "capturas" / "nivel2.png").as_uri()
    hoy = date.today().strftime("%d/%m/%Y")
    pagina = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Toonaria — Game Design Document</title><style>{CSS}</style></head><body>
<section class="portada">
  <img class="logo" src="{logo}" alt="Toonaria">
  <div class="tipo">Game Design Document</div>
  <img class="captura" src="{captura}" alt="Barrio de los Teatros">
  <div class="datos"><b>Grupo 11</b> — Fernando Rodríguez · Mateo Fernández ·
  Natalia Ailén González · Fernando Rubén Bareiro Ruiz</div>
  <div class="datos">Multimedia y Juegos en Web · Tecnicatura Universitaria en Desarrollo Web<br>
  Facultad de Ciencias de la Administración · Universidad Nacional de Entre Ríos</div>
  <div class="datos">{hoy}</div>
</section>
<section class="indice"><h2>Índice</h2><ol>{indice}</ol></section>
{html}
</body></html>"""
    salida.write_text(pagina, encoding="utf8")
    print("html", salida, len(titulos), "secciones")


if __name__ == "__main__":
    main()
