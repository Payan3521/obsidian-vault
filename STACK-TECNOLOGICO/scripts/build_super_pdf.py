#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, json, html, subprocess
from datetime import datetime

# Rutas del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import knowledge_base
import tech_expert_system

INVENTORY_PATH = "/tmp/vault_inventory.json"
HTML_OUTPUT = "/tmp/super_stack_tecnologico.html"
PDF_OUTPUT = "/home/payan/Documentos/Obsidian Vault/STACK-TECNOLOGICO/Super_Stack_Tecnologico_Ingenieria_Software.pdf"

print("Cargando inventario de notas...")
with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
    inv = json.load(f)

categories = inv["categories"]
topics = inv["topics"]

# Agrupar topics por categoría
topics_by_folder = {}
for t in topics:
    fldr = t["folder"]
    if fldr not in topics_by_folder:
        topics_by_folder[fldr] = []
    topics_by_folder[fldr].append(t)

print(f"Total categorías cargadas: {len(categories)}")
print(f"Total tecnologías y conceptos cargados: {len(topics)}")

# Generar HTML con diseño editorial impecable
html_parts = []

html_parts.append("""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Súper Stack Tecnológico — Enciclopedia Integral de Ingeniería de Software</title>
<style>
    @page {
        size: A4;
        margin: 18mm 16mm 20mm 16mm;
        @bottom-right {
            content: counter(page);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 8.5pt;
            color: #64748b;
        }
        @bottom-left {
            content: "Súper Stack Tecnológico — Toda la Ingeniería de Software";
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 8.5pt;
            color: #94a3b8;
        }
    }

    * { box-sizing: border-box; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #0f172a;
        background-color: #ffffff;
        line-height: 1.5;
        font-size: 10pt;
        margin: 0;
        padding: 0;
    }

    /* Portada */
    .cover-page {
        page-break-after: always;
        height: 92vh;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 40px 20px;
        background: linear-gradient(145deg, #0f172a 0%, #1e293b 50%, #0369a1 100%);
        color: #ffffff;
        border-radius: 12px;
    }
    .cover-badge {
        display: inline-block;
        padding: 6px 16px;
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 9999px;
        font-size: 10pt;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .cover-title {
        font-size: 34pt;
        font-weight: 900;
        line-height: 1.15;
        margin-top: 24px;
        color: #f8fafc;
        letter-spacing: -0.02em;
    }
    .cover-subtitle {
        font-size: 16pt;
        color: #94a3b8;
        margin-top: 14px;
        font-weight: 400;
        max-width: 90%;
        line-height: 1.4;
    }
    .cover-stats {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 40px;
        padding: 20px;
        background: rgba(15, 23, 42, 0.6);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stat-number {
        font-size: 26pt;
        font-weight: 800;
        color: #38bdf8;
    }
    .stat-label {
        font-size: 9pt;
        color: #cbd5e1;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .cover-footer {
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        padding-top: 16px;
        display: flex;
        justify-content: space-between;
        font-size: 9.5pt;
        color: #cbd5e1;
    }

    /* Tabla de contenidos */
    .toc-page {
        page-break-after: always;
        padding: 20px 0;
    }
    .toc-title {
        font-size: 22pt;
        font-weight: 800;
        color: #0f172a;
        border-bottom: 3px solid #0284c7;
        padding-bottom: 10px;
        margin-bottom: 24px;
    }
    .toc-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px 24px;
    }
    .toc-item {
        font-size: 9pt;
        display: flex;
        justify-content: space-between;
        border-bottom: 1px dotted #cbd5e1;
        padding-bottom: 4px;
    }
    .toc-item strong { color: #0284c7; margin-right: 6px; }

    /* Separador de Carpeta / Módulo */
    .folder-header-block {
        page-break-before: always;
        margin-top: 10px;
        margin-bottom: 24px;
        padding: 24px;
        background: #f8fafc;
        border-left: 6px solid #0284c7;
        border-radius: 0 10px 10px 0;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }
    .folder-semester-tag {
        font-size: 9pt;
        font-weight: 800;
        color: #0284c7;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .folder-title {
        font-size: 20pt;
        font-weight: 900;
        color: #0f172a;
        margin: 6px 0 12px 0;
        letter-spacing: -0.01em;
    }
    .folder-desc-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 14px;
        font-size: 9.5pt;
    }
    .folder-desc-box {
        background: #ffffff;
        padding: 12px 14px;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    .folder-desc-label {
        font-size: 8pt;
        font-weight: 800;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 4px;
        display: block;
        letter-spacing: 0.05em;
    }

    /* Fichas técnicas de tecnologías */
    .tech-card {
        page-break-inside: avoid;
        margin-bottom: 20px;
        padding: 18px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .card-deep {
        border-left: 5px solid #0284c7;
        background: #ffffff;
    }
    .card-guide {
        border-left: 5px solid #eab308;
        background: #fffdf7;
    }
    .card-standard {
        border-left: 4px solid #94a3b8;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f5f9;
    }
    .title-wrap {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .tech-badge {
        align-self: flex-start;
        display: inline-block;
        font-size: 7.5pt;
        font-weight: 800;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 4px;
        letter-spacing: 0.05em;
    }
    .badge-deep { background: #e0f2fe; color: #0369a1; }
    .badge-star { background: #fef08a; color: #854d0e; }
    .badge-standard { background: #f1f5f9; color: #475569; }
    .badge-category { background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; margin-left: 4px; }
    
    .tech-title {
        font-size: 14pt;
        font-weight: 800;
        color: #0f172a;
        margin: 2px 0 0 0;
    }
    
    .card-rels {
        font-size: 8pt;
        color: #64748b;
        text-align: right;
        max-width: 45%;
    }
    .rels-title { font-weight: 700; color: #475569; }
    .rel-tag {
        display: inline-block;
        background: #f1f5f9;
        color: #334155;
        padding: 1px 6px;
        border-radius: 3px;
        margin: 2px;
    }

    .card-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 10px;
    }
    .card-block {
        margin-bottom: 10px;
    }
    .block-label {
        font-size: 7.5pt;
        font-weight: 800;
        text-transform: uppercase;
        color: #475569;
        letter-spacing: 0.06em;
        display: block;
        margin-bottom: 3px;
    }
    .card-block p {
        margin: 0;
        font-size: 9pt;
        color: #1e293b;
        line-height: 1.45;
        text-align: justify;
    }

    pre {
        background: #0f172a;
        color: #f8fafc;
        padding: 10px 12px;
        border-radius: 6px;
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 7.5pt;
        line-height: 1.35;
        overflow-x: auto;
        margin: 4px 0 0 0;
    }
    code { font-family: monospace; font-size: 8.5pt; }

    .guide-section {
        margin-bottom: 8px;
    }
    .guide-section strong {
        color: #0369a1;
        font-size: 8.5pt;
    }
</style>
</head>
<body>
""")

# 1. Portada
now_str = datetime.now().strftime("%d de noviembre de %Y")
html_parts.append(f"""
<div class="cover-page">
    <div>
        <span class="cover-badge">Enciclopedia & Compendio Definitivo</span>
        <h1 class="cover-title">Súper Stack Tecnológico<br>Ingeniería de Software Integral</h1>
        <p class="cover-subtitle">
            Manual exhaustivo de referencia: cada carpeta, tecnología, herramienta y concepto explicados a profundidad técnica respondiendo rigurosamente <strong>¿Qué es?</strong>, <strong>¿Para qué sirve?</strong> y <strong>¿Cómo funciona internamente?</strong>.
        </p>
        
        <div class="cover-stats">
            <div>
                <div class="stat-number">49</div>
                <div class="stat-label">Carpetas Temáticas</div>
            </div>
            <div>
                <div class="stat-number">{len(topics)}</div>
                <div class="stat-label">Tecnologías Explicadas</div>
            </div>
            <div>
                <div class="stat-number">8</div>
                <div class="stat-label">Semestres + Núcleo</div>
            </div>
            <div>
                <div class="stat-number">100%</div>
                <div class="stat-label">Rigor Técnico</div>
            </div>
        </div>
    </div>
    
    <div class="cover-footer">
        <div>Vault: <code>STACK-TECNOLOGICO</code> &middot; Generado para ingeniería de software</div>
        <div>Fecha: {now_str} &middot; Edición Profesional Maestra</div>
    </div>
</div>
""")

# 2. Índice General
html_parts.append("""
<div class="toc-page">
    <h2 class="toc-title">Índice General de Carpetas y Dominios</h2>
    <div class="toc-grid">
""")
for idx, cat in enumerate(categories, 1):
    f_meta = knowledge_base.FOLDER_METADATA.get(cat, {})
    title = f_meta.get("title", cat.replace("-", " ").title())
    count = len(topics_by_folder.get(cat, []))
    html_parts.append(f"""
        <div class="toc-item">
            <span><strong>{idx:02d}.</strong> {html.escape(title)}</span>
            <span>{count} notas</span>
        </div>
    """)
html_parts.append("""
    </div>
</div>
""")

# 3. Contenido de Carpetas y Tecnologías
print("Generando módulos y fichas técnicas exhaustivas...")
for idx, cat in enumerate(categories, 1):
    f_meta = knowledge_base.FOLDER_METADATA.get(cat, {
        "title": cat.replace("-", " ").title(),
        "semester": "Módulo de Ingeniería",
        "role": f"Dominio especializado en {cat.replace('-', ' ')}.",
        "why": "Componente indispensable del stack tecnológico moderno para garantizar escalabilidad, seguridad y fiabilidad.",
        "internal_mechanics": "Opera mediante abstracciones, protocolos estandarizados e interfaces de comunicación optimizadas para el rendimiento del sistema."
    })
    
    folder_topics = topics_by_folder.get(cat, [])
    
    # Encabezado de la Carpeta
    html_parts.append(f"""
    <div class="folder-header-block">
        <span class="folder-semester-tag">{html.escape(f_meta.get('semester', 'Ingeniería de Software'))} &middot; Carpeta {idx:02d}</span>
        <h2 class="folder-title">{html.escape(f_meta.get('title', cat))} ({len(folder_topics)} Tecnologías)</h2>
        <div class="folder-desc-grid">
            <div class="folder-desc-box">
                <span class="folder-desc-label">Rol en la Ingeniería de Software</span>
                <p>{html.escape(f_meta.get('role', ''))}</p>
            </div>
            <div class="folder-desc-box">
                <span class="folder-desc-label">¿Por qué es imprescindible dominarlo?</span>
                <p>{html.escape(f_meta.get('why', ''))}</p>
            </div>
        </div>
        <div class="folder-desc-box" style="margin-top: 10px;">
            <span class="folder-desc-label">Mecanismos Internos y Arquitectura Subyacente</span>
            <p>{html.escape(f_meta.get('internal_mechanics', ''))}</p>
        </div>
    </div>
    """)
    
    # Fichas técnicas de cada tecnología de la carpeta
    for t in folder_topics:
        card_html = tech_expert_system.generate_technical_card(t["name"], cat, f_meta, t)
        html_parts.append(card_html)

html_parts.append("""
</body>
</html>
""")

print("Escribiendo archivo HTML consolidado...")
with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
    f.write("".join(html_parts))

print(f"HTML generado exitosamente en {HTML_OUTPUT} ({os.path.getsize(HTML_OUTPUT)} bytes)")
