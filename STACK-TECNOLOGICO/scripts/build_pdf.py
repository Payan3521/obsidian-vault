#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de los "Súper PDF" de los vaults STACK-TECNOLOGICO y SECDEV.

Uso:
    python3 build_pdf.py STACK-TECNOLOGICO
    python3 build_pdf.py SECDEV
    python3 build_pdf.py all

Fuentes:
  - Las notas .md del vault (estructura, nivel, relaciones, contexto y guías completas).
  - scripts/contenido/<VAULT>/*.json   → fichas técnicas (qué es / para qué / cómo / prácticas / ejemplo).
  - scripts/contenido/<VAULT>/_carpetas.json → introducción de cada carpeta.
Si una nota nueva no tiene ficha todavía, aparece igual con su contexto y la marca "ficha pendiente".
"""
import os, re, sys, json, glob, html, subprocess, shutil
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inventario  # noqa: E402

ROOT = inventario.ROOT
CONTENT = os.path.join(HERE, "contenido")
CHROMIUM = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")

CONFIG = {
    "STACK-TECNOLOGICO": {
        "titulo": "Stack Tecnológico",
        "subtitulo": "Toda la ingeniería de software, explicada: cada carpeta, cada tecnología, cada concepto",
        "kicker": "Enciclopedia de ingeniería de software",
        "accent": "#0369a1", "accent2": "#38bdf8", "dark": "#0b1424",
        "pdf": os.path.join(ROOT, "STACK-TECNOLOGICO", "Super_Stack_Tecnologico_Ingenieria_Software.pdf"),
        "orden": [  # orden de lectura (semestres + núcleo profesional); lo no listado va al final
            "fundamentos-de-programación", "principios-de-ingeniería-de-software", "matemáticas-i", "física-i-mecánica",
            "lenguajes-runtimes-y-build", "álgebra-lineal", "matemáticas-ii", "física-ii-electromagnetismo",
            "ética-y-legalidad-profesional", "estructuras-de-datos-y-algoritmos", "desarrollo-de-software",
            "ingeniería-de-requisitos", "matemáticas-iii", "diseño-de-interfaces-de-usuario", "estadística-y-probabilidad",
            "bases-de-datos", "matemáticas-iv", "construcción-de-app-empresariales", "ingeniería-de-software-i",
            "construcción-de-apps-móviles", "desarrollo-web", "sistemas-operativos-lo-que-deberías-saber-hoy",
            "redes-de-datos-vista-práctica-y-moderna", "ingeniería-de-software-ii", "matemática-discreta",
            "sistemas-distribuidos", "infraestructura-de-ti", "desarrollo-en-equipo", "simulación", "compiladores",
            "gestión-de-proyectos-de-ti", "economía-del-software", "liderazgo-técnico-y-gestión-de-personas",
            "temas-avanzados-de-ingeniería-de-software",
            "control-de-versiones-y-flujo-de-código", "frameworks-y-librerías", "formatos-y-serialización",
            "apis-e-integraciones", "arquitectura-y-diseño", "arquitecturas-de-software-uml-c4-adr", "arquitectura",
            "testing", "contenerización-y-orquestación", "devops-ci-cd-e-iac", "cloud-aws", "hosting-paas-y-plataformas",
            "caching-y-mensajería", "observabilidad", "seguridad", "ia-nueva-era-sección-ampliada",
            "ingeniería-de-prompts-avanzada", "context-engineering", "datos-para-ia", "fine-tuning-y-adaptación-avanzada",
            "inferencia-y-optimización-de-modelos", "evaluación-y-calidad-de-ia", "llmops-y-ciclo-de-vida",
            "agentes-avanzados-y-nuevas-formas-de-trabajar", "herramientas-y-plataformas-de-ia-complemento",
            "producto-ux-y-negocio-de-ia", "criterio-y-estrategia-de-ia-en-el-trabajo",
            "productividad-conocimiento-y-colaboración", "documentacion",
        ],
    },
    "SECDEV": {
        "titulo": "SECDEV",
        "subtitulo": "Seguridad informática aplicada al software: AppSec y DevSecOps de punta a punta",
        "kicker": "Enciclopedia de especialización en seguridad",
        "accent": "#b91c1c", "accent2": "#f87171", "dark": "#1a0b0e",
        "pdf": os.path.join(ROOT, "SECDEV", "Super_SECDEV_Seguridad_Software.pdf"),
        "orden": [
            "fundamentos-de-seguridad-de-software", "seguridad-en-el-ciclo-de-vida-del-software",
            "modelado-de-amenazas-y-requisitos", "arquitectura-y-diseño-seguros", "owasp-y-vulnerabilidades-web",
            "código-seguro-por-lenguaje-y-framework", "autenticación-identidad-y-sesiones",
            "autorización-y-control-de-acceso", "criptografía-aplicada", "gestión-de-secretos-y-claves",
            "seguridad-de-apis-e-integraciones", "seguridad-frontend-y-navegador", "seguridad-en-bases-de-datos-y-datos",
            "seguridad-móvil", "seguridad-de-redes-aplicada", "seguridad-en-cloud", "seguridad-serverless",
            "seguridad-en-contenedores-y-orquestación", "seguridad-en-iac-y-pipelines-ci-cd",
            "seguridad-en-ia-llm-y-agentes", "seguridad-en-ia-avanzada-agentes-contexto-y-voz", "seguridad-iot-y-ot", "pruebas-y-análisis-de-seguridad",
            "herramientas-y-laboratorio-de-appsec", "registro-monitoreo-y-detección", "threat-hunting",
            "respuesta-a-incidentes-y-forense-digital", "riesgo-gobierno-y-cultura", "privacidad-legal-y-cumplimiento",
        ],
    },
}

esc = lambda s: html.escape(str(s or ""))


def rich(s):
    """Escapa y convierte `código` y **negrita** en HTML."""
    t = esc(s)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)


def slug(s):
    s = re.sub(r"[^\w]+", "-", s.lower(), flags=re.U).strip("-")
    return s or "x"


def load_content(vault):
    fichas, carpetas = {}, {}
    d = os.path.join(CONTENT, vault)
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            data = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            print(f"  ⚠ JSON inválido {os.path.basename(p)}: {e}")
            continue
        if os.path.basename(p).startswith("_carpetas"):
            carpetas.update(data)
        else:
            folder = os.path.basename(p).rsplit("__", 1)[0]
            for k, v in data.items():
                fichas[(folder, k)] = v
                fichas.setdefault(("*", k), v)
    return fichas, carpetas


def md_to_html(md):
    md = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", md)
    md = re.sub(r"\[\[([^\]]+)\]\]", r"\1", md)
    md = re.sub(r"^# .*\n", "", md, count=1, flags=re.M)
    md = re.sub(r"## Mis notas.*", "", md, flags=re.S)
    try:
        out = subprocess.run(["pandoc", "-f", "gfm", "-t", "html", "--shift-heading-level-by=2"],
                             input=md, capture_output=True, text=True, timeout=60)
        if out.returncode == 0:
            return out.stdout
    except Exception:
        pass
    return "<pre>" + esc(md) + "</pre>"


def card(vault, folder, n, ficha, anchors):
    name = n["name"]
    aid = anchors[(folder, name)]
    badges = []
    if n["estrella"] or n["nivel"] == "dominar":
        badges.append('<span class="b b-star">⭐ Dominar</span>')
    else:
        badges.append('<span class="b b-know">Conocer</span>')
    if n["guia"]:
        badges.append('<span class="b b-guide">Guía completa</span>')
    rel_links = []
    for r in n["relacionados"][:6]:
        target = anchors.get((folder, r)) or anchors.get(("*", r))
        rel_links.append(f'<a href="#{target}">{esc(r)}</a>' if target else f"<span>{esc(r)}</span>")
    rels = " · ".join(rel_links)

    parts = [f'<article class="card" id="{aid}">',
             f'<header><div class="badges">{"".join(badges)}</div><h3>{esc(name)}</h3></header>']
    if ficha:
        parts.append('<div class="grid2">'
                     f'<section class="q"><h4>¿Qué es?</h4><p>{rich(ficha.get("que"))}</p></section>'
                     f'<section class="q"><h4>¿Para qué sirve?</h4><p>{rich(ficha.get("para"))}</p></section></div>')
        parts.append(f'<section class="q how"><h4>¿Cómo funciona?</h4><p>{rich(ficha.get("como"))}</p></section>')
        pr = ficha.get("practicas") or []
        if isinstance(pr, str):
            pr = [pr]
        ej = (ficha.get("ejemplo") or "").strip()
        if pr or ej:
            parts.append('<div class="grid2">' if (pr and ej) else "<div>")
            if pr:
                parts.append('<section class="q tips"><h4>Buenas prácticas y trampas</h4><ul>'
                             + "".join(f"<li>{rich(x)}</li>" for x in pr) + "</ul></section>")
            if ej:
                parts.append(f'<section class="q ex"><h4>Ejemplo</h4><pre>{esc(ej)}</pre></section>')
            parts.append("</div>")
        if ficha.get("entrevista"):
            parts.append(f'<p class="interview"><b>En una entrevista:</b> {rich(ficha["entrevista"])}</p>')
    else:
        parts.append(f'<p class="pending">Ficha pendiente. Contexto en el mapa: {esc(n["contexto"])}</p>')
    if n["guia"] and n["body"]:
        parts.append('<details class="guide"><h4 class="guide-h">Guía completa del vault</h4>'
                     f'<div class="guide-body">{md_to_html(n["body"])}</div></details>')
    if rels:
        parts.append(f'<footer>Se conecta con: {rels}</footer>')
    parts.append("</article>")
    return "".join(parts)


CSS = """
@page { size: A4; margin: 15mm 14mm 16mm 14mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Inter','Noto Sans','DejaVu Sans',system-ui,sans-serif; color:#0f172a; font-size:9.6pt; line-height:1.5; margin:0; }
a { color: var(--accent); text-decoration: none; }
h1,h2,h3,h4 { letter-spacing:-0.01em; }
.cover { height: 266mm; padding: 22mm 18mm; color:#fff; border-radius: 6mm; page-break-after: always;
  background: radial-gradient(circle at 85% 15%, var(--accent2) 0%, transparent 38%),
              linear-gradient(150deg, var(--dark) 0%, #111827 55%, var(--accent) 140%);
  display:flex; flex-direction:column; justify-content:space-between; }
.kicker { display:inline-block; border:1px solid rgba(255,255,255,.35); border-radius:99px; padding:5px 14px;
  font-size:8.5pt; letter-spacing:.14em; text-transform:uppercase; font-weight:700; color: var(--accent2); }
.cover h1 { font-size: 46pt; line-height:1.02; margin: 18mm 0 6mm; font-weight: 900; }
.cover .sub { font-size: 15pt; color:#cbd5e1; max-width: 150mm; line-height:1.35; }
.stats { display:grid; grid-template-columns: repeat(4,1fr); gap:5mm; margin-top: 14mm; }
.stat { background: rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.12); border-radius:4mm; padding:5mm; }
.stat b { display:block; font-size: 26pt; color: var(--accent2); font-weight:900; }
.stat span { font-size: 8pt; text-transform: uppercase; letter-spacing:.08em; color:#e2e8f0; }
.cover .foot { font-size: 8.5pt; color:#94a3b8; border-top:1px solid rgba(255,255,255,.15); padding-top:4mm; display:flex; justify-content:space-between; }
.page { page-break-before: always; }
.h-part { font-size: 9pt; letter-spacing:.16em; text-transform:uppercase; color: var(--accent); font-weight:800; }
h2.big { font-size: 24pt; margin: 2mm 0 6mm; border-bottom: 3px solid var(--accent); padding-bottom: 3mm; }
.toc-part { margin: 5mm 0 2mm; font-weight:800; color: var(--accent); font-size: 10pt; text-transform: uppercase; letter-spacing:.08em; }
.toc a { display:flex; justify-content:space-between; color:#0f172a; border-bottom:1px dotted #cbd5e1; padding:1.2mm 0; font-size: 9.5pt; }
.toc a span:last-child { color:#64748b; }
.howto { display:grid; grid-template-columns: 1fr 1fr; gap:5mm; }
.box { border:1px solid #e2e8f0; border-radius:3mm; padding:4mm 5mm; background:#f8fafc; }
.box h4 { margin:0 0 1.5mm; color: var(--accent); font-size: 10pt; }
.box p { margin:0; }
table.over { width:100%; border-collapse: collapse; font-size: 8.6pt; }
table.over th { text-align:left; background: var(--dark); color:#fff; padding: 2mm; }
table.over td { border-bottom:1px solid #e2e8f0; padding: 2mm; vertical-align: top; }
table.over tr { page-break-inside: avoid; }
.core { columns: 3; column-gap: 6mm; font-size: 9.2pt; }
.core a { display:block; padding: .8mm 0; color:#0f172a; }
.part-page { page-break-before: always; height: 250mm; display:flex; flex-direction:column; justify-content:center;
  border-left: 8px solid var(--accent); padding-left: 12mm; }
.part-page .n { font-size: 11pt; letter-spacing:.2em; color: var(--accent); font-weight: 800; text-transform: uppercase; }
.part-page h2 { font-size: 34pt; margin: 3mm 0 6mm; }
.part-page li { font-size: 11pt; margin: 1mm 0; }
.chapter { page-break-before: always; }
.ch-head { background: linear-gradient(135deg, var(--dark), #1f2937); color:#fff; border-radius:4mm; padding: 7mm 8mm; margin-bottom: 5mm; }
.ch-head .num { color: var(--accent2); font-weight: 800; font-size: 9pt; letter-spacing:.16em; text-transform: uppercase; }
.ch-head h2 { font-size: 22pt; margin: 2mm 0 1mm; }
.ch-head .meta { color:#cbd5e1; font-size: 9pt; }
.ch-intro { display:grid; grid-template-columns: 1fr 1fr; gap: 4mm; margin-bottom: 4mm; }
.ch-intro .box p { font-size: 9.2pt; }
.ch-index { font-size: 8.6pt; columns: 3; column-gap: 5mm; border:1px solid #e2e8f0; border-radius: 3mm; padding: 3mm 4mm; margin-bottom: 6mm; }
.ch-index a { display:block; color:#334155; padding:.4mm 0; }
.card { border:1px solid #e2e8f0; border-left: 4px solid var(--accent); border-radius: 3mm; padding: 4mm 5mm; margin: 0 0 4.5mm; page-break-inside: avoid; background:#fff; }
.card header { display:flex; align-items:baseline; gap: 3mm; border-bottom:1px solid #f1f5f9; padding-bottom: 2mm; margin-bottom: 2.5mm; flex-wrap: wrap; }
.card h3 { margin:0; font-size: 13pt; order: 1; }
.badges { order: 2; display:flex; gap: 1.5mm; }
.b { font-size: 7pt; font-weight: 800; text-transform: uppercase; letter-spacing: .06em; padding: .6mm 2mm; border-radius: 99px; }
.b-star { background:#fef3c7; color:#92400e; } .b-know { background:#f1f5f9; color:#475569; } .b-guide { background:#dcfce7; color:#166534; }
.grid2 { display:grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.q h4 { margin: 1.5mm 0 .8mm; font-size: 7.6pt; text-transform: uppercase; letter-spacing: .09em; color: var(--accent); }
.q p { margin: 0; text-align: justify; }
.q code, .interview code, .box code { background:#f1f5f9; color:#0f172a; padding:0 1mm; border-radius:1mm; font-size:8.2pt; font-family:'DejaVu Sans Mono',monospace; }
.q ul { margin: 0; padding-left: 4.5mm; } .q li { margin: .5mm 0; }
pre { background:#0f172a; color:#e2e8f0; border-radius: 2mm; padding: 2.5mm 3mm; font-family: 'JetBrains Mono','Fira Code','DejaVu Sans Mono',monospace;
  font-size: 7.3pt; line-height:1.4; white-space: pre-wrap; word-break: break-word; margin: 0; }
.interview { margin: 2.5mm 0 0; background: #f8fafc; border-left: 3px solid var(--accent2); padding: 1.8mm 3mm; font-size: 8.8pt; font-style: italic; }
.interview b { font-style: normal; color: var(--accent); }
.card footer { margin-top: 2.5mm; font-size: 8pt; color:#64748b; }
.pending { color:#64748b; font-style: italic; }
.guide { display:block; margin-top: 3mm; border-top: 1px dashed #cbd5e1; padding-top: 2mm; }
.card:has(.guide) { page-break-inside: auto; }
.guide-h { color:#166534; font-size: 9pt; text-transform: uppercase; letter-spacing: .08em; margin: 1mm 0; }
.guide-body { font-size: 8.8pt; }
.guide-body h3, .guide-body h4, .guide-body h5 { color: var(--accent); margin: 3mm 0 1mm; font-size: 10pt; }
.guide-body table { border-collapse: collapse; width:100%; font-size: 8pt; margin: 2mm 0; }
.guide-body td, .guide-body th { border:1px solid #e2e8f0; padding: 1mm 1.5mm; vertical-align: top; }
.guide-body th { background:#f1f5f9; }
.guide-body code { background:#f1f5f9; padding: 0 1mm; border-radius: 1mm; font-size: 8pt; }
.guide-body pre code { background: none; padding:0; color: inherit; }
.guide-body blockquote { border-left: 3px solid var(--accent2); margin: 2mm 0; padding: 0 3mm; color:#334155; }
.gloss { columns: 2; column-gap: 7mm; font-size: 8.4pt; }
.gloss .L { font-weight: 900; color: var(--accent); font-size: 13pt; margin: 3mm 0 1mm; break-after: avoid; }
.gloss a { display:block; color:#0f172a; padding:.3mm 0; break-inside: avoid; }
.gloss a i { color:#64748b; font-style: normal; }
"""


def build(vault):
    cfg = CONFIG[vault]
    inv = inventario.build()[vault]
    fichas, carpetas = load_content(vault)
    orden = [f for f in cfg["orden"] if f in inv] + sorted(f for f in inv if f not in cfg["orden"])

    anchors = {}
    for f in orden:
        for n in inv[f]:
            a = f"n-{slug(f)}-{slug(n['name'])}"
            anchors[(f, n["name"])] = a
            anchors.setdefault(("*", n["name"]), a)

    total = sum(len(inv[f]) for f in orden)
    con_ficha = sum(1 for f in orden for n in inv[f] if fichas.get((f, n["name"])) or fichas.get(("*", n["name"])))
    estrellas = sorted({(n["name"], f) for f in orden for n in inv[f] if n["estrella"] or n["nivel"] == "dominar"})
    guias = sum(1 for f in orden for n in inv[f] if n["guia"])

    def ctitle(f):
        return (carpetas.get(f) or {}).get("titulo") or f.replace("-", " ").capitalize()

    # agrupar en partes
    grupos, gorder = {}, []
    for f in orden:
        g = (carpetas.get(f) or {}).get("grupo") or "Otros temas"
        if g not in grupos:
            grupos[g] = []
            gorder.append(g)
        grupos[g].append(f)
    chap_num = {f: i for i, f in enumerate([f for g in gorder for f in grupos[g]], 1)}

    H = [f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>{esc(cfg['titulo'])} — {esc(cfg['kicker'])}</title>
<style>:root{{--accent:{cfg['accent']};--accent2:{cfg['accent2']};--dark:{cfg['dark']};}}{CSS}</style></head><body>"""]

    H.append(f"""<section class="cover"><div><span class="kicker">{esc(cfg['kicker'])}</span>
<h1>{esc(cfg['titulo'])}</h1><p class="sub">{esc(cfg['subtitulo'])}</p>
<div class="stats"><div class="stat"><b>{len(orden)}</b><span>Carpetas / capítulos</span></div>
<div class="stat"><b>{total}</b><span>Temas explicados</span></div>
<div class="stat"><b>{len(estrellas)}</b><span>⭐ Núcleo a dominar</span></div>
<div class="stat"><b>{guias or len(gorder)}</b><span>{"Guías completas" if guias else "Partes del libro"}</span></div></div></div>
<div class="foot"><span>Generado desde el vault <b>{esc(vault)}/</b> de Obsidian</span><span>Edición del {date.today().strftime('%d/%m/%Y')}</span></div></section>""")

    # índice
    H.append('<section class="page toc"><div class="h-part">Contenido</div><h2 class="big">Índice</h2>'
             '<a href="#como-leer"><span>Cómo leer este libro</span><span></span></a>'
             '<a href="#panorama"><span>Panorama: todas las carpetas de un vistazo</span><span></span></a>'
             '<a href="#nucleo"><span>⭐ El núcleo a dominar</span><span></span></a>')
    for gi, g in enumerate(gorder, 1):
        H.append(f'<div class="toc-part"><a href="#parte-{gi}" style="border:0;color:inherit">Parte {gi} · {esc(g)}</a></div>')
        for f in grupos[g]:
            H.append(f'<a href="#c-{slug(f)}"><span>{chap_num[f]:02d}. {esc(ctitle(f))}</span><span>{len(inv[f])} temas</span></a>')
    H.append('<div class="toc-part"><a href="#glosario" style="border:0;color:inherit">Glosario A–Z</a></div></section>')

    # cómo leer
    H.append(f"""<section class="page" id="como-leer"><div class="h-part">Antes de empezar</div><h2 class="big">Cómo leer este libro</h2>
<p>Cada carpeta del vault es un <b>capítulo</b>. Cada capítulo abre con una introducción (qué cubre, por qué importa, cómo encaja con el resto y por dónde empezar) y sigue con una <b>ficha por cada tema</b> que responde siempre las mismas preguntas:</p>
<div class="howto">
<div class="box"><h4>¿Qué es?</h4><p>Definición técnica precisa, sin rodeos.</p></div>
<div class="box"><h4>¿Para qué sirve?</h4><p>El problema real que resuelve y cuándo se usa.</p></div>
<div class="box"><h4>¿Cómo funciona?</h4><p>El mecanismo interno: componentes, flujo, protocolos, algoritmos.</p></div>
<div class="box"><h4>Buenas prácticas y ejemplo</h4><p>Trampas típicas, comparaciones, un snippet o caso concreto y una frase para entrevistas.</p></div>
</div>
<h3>Niveles</h3>
<div class="howto"><div class="box"><h4>⭐ Dominar</h4><p>Lo usas cada semana y lo defenderías en una entrevista.</p></div>
<div class="box"><h4>Conocer</h4><p>Sabes qué es y cuándo usarlo, aunque no lo configures de memoria.</p></div></div>
<p style="margin-top:5mm">Todo es <b>clicable</b>: el índice, los temas relacionados al pie de cada ficha y el glosario final te llevan directo a la ficha. El PDF también trae marcadores (panel lateral del lector).</p>
<p><b>Es un mapa, no un examen:</b> nadie domina los {total} temas. Lee una vez para reconocer, profundiza en tu núcleo y en tu especialidad.</p></section>""")

    # panorama
    H.append('<section class="page" id="panorama"><div class="h-part">Panorama</div><h2 class="big">Todas las carpetas de un vistazo</h2>'
             '<table class="over"><tr><th>#</th><th>Carpeta</th><th>Qué cubre</th><th>Temas</th></tr>')
    for g in gorder:
        for f in grupos[g]:
            H.append(f'<tr><td>{chap_num[f]:02d}</td><td><a href="#c-{slug(f)}"><b>{esc(ctitle(f))}</b></a><br><small>{esc(g)}</small></td>'
                     f'<td>{esc((carpetas.get(f) or {}).get("rol", ""))}</td><td>{len(inv[f])}</td></tr>')
    H.append("</table></section>")

    # núcleo
    H.append('<section class="page" id="nucleo"><div class="h-part">Prioridad</div><h2 class="big">⭐ El núcleo a dominar</h2>'
             '<p>Estos temas son la columna vertebral. Si solo tienes tiempo para una parte del libro, empieza aquí.</p><div class="core">')
    for name, f in estrellas:
        H.append(f'<a href="#{anchors[(f, name)]}">⭐ {esc(name)}</a>')
    H.append("</div></section>")

    # partes y capítulos
    for gi, g in enumerate(gorder, 1):
        H.append(f'<section class="part-page" id="parte-{gi}"><div class="n">Parte {gi}</div><h2>{esc(g)}</h2><ul>'
                 + "".join(f'<li><a href="#c-{slug(f)}">{chap_num[f]:02d}. {esc(ctitle(f))}</a></li>' for f in grupos[g])
                 + "</ul></section>")
        for f in grupos[g]:
            c = carpetas.get(f) or {}
            notes = sorted(inv[f], key=lambda n: (not (n["estrella"] or n["nivel"] == "dominar"), n["name"].lower()))
            H.append(f'<section class="chapter" id="c-{slug(f)}"><div class="ch-head"><div class="num">Capítulo {chap_num[f]:02d} · {esc(g)}</div>'
                     f'<h2>{esc(ctitle(f))}</h2><div class="meta">Carpeta <code>{esc(f)}/</code> · {len(notes)} temas</div></div>')
            if c:
                H.append('<div class="ch-intro">'
                         f'<div class="box"><h4>Qué cubre</h4><p>{esc(c.get("rol"))}</p></div>'
                         f'<div class="box"><h4>Por qué importa</h4><p>{esc(c.get("por_que"))}</p></div>'
                         f'<div class="box"><h4>Cómo encaja</h4><p>{esc(c.get("como_encaja"))}</p></div>'
                         f'<div class="box"><h4>Ruta de estudio</h4><p>{esc(c.get("ruta"))}</p></div></div>')
            H.append('<div class="ch-index">' + "".join(
                f'<a href="#{anchors[(f, n["name"])]}">{"⭐ " if (n["estrella"] or n["nivel"] == "dominar") else ""}{esc(n["name"])}</a>'
                for n in notes) + "</div>")
            for n in notes:
                fi = fichas.get((f, n["name"])) or fichas.get(("*", n["name"]))
                H.append(card(vault, f, n, fi, anchors))
            H.append("</section>")

    # glosario
    H.append('<section class="page" id="glosario"><div class="h-part">Referencia</div><h2 class="big">Glosario A–Z</h2><div class="gloss">')
    allnames = sorted({(n["name"], f) for f in orden for n in inv[f]},
                      key=lambda x: (x[0].lower().lstrip(".¿¡(\"'"), x[1]))
    last = None
    import unicodedata
    for name, f in allnames:
        L = unicodedata.normalize("NFD", name.lstrip(".¿¡(\"'")[:1].upper())[:1]
        L = L if L.isalpha() else "#"
        if L != last:
            H.append(f'<div class="L">{L}</div>')
            last = L
        H.append(f'<a href="#{anchors[(f, name)]}">{esc(name)} <i>— {esc(ctitle(f))}</i></a>')
    H.append("</div></section></body></html>")

    html_path = f"/tmp/super_{slug(vault)}.html"
    open(html_path, "w", encoding="utf-8").write("".join(H))
    print(f"[{vault}] {len(orden)} carpetas · {total} temas · {con_ficha} con ficha ({total - con_ficha} pendientes) · HTML {os.path.getsize(html_path)//1024} KB")
    return html_path, cfg["pdf"]


def to_pdf(html_path, pdf_path):
    cmd = [CHROMIUM, "--headless", "--disable-gpu", "--no-sandbox", "--user-data-dir=/tmp/chromium-pdf-data",
           "--no-pdf-header-footer", "--generate-pdf-document-outline", "--run-all-compositor-stages-before-draw",
           f"--print-to-pdf={pdf_path}", "file://" + html_path]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = list(CONFIG) if arg == "all" else [arg]
    only_html = "--html" in sys.argv
    for v in targets:
        h, p = build(v)
        if not only_html:
            to_pdf(h, p)
            print(f"  → {p}")

