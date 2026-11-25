#!/usr/bin/env python3
"""Inventario de notas de los vaults STACK-TECNOLOGICO y SECDEV."""
import os, re, json, glob
ROOT = "/home/payan/Documentos/Obsidian Vault"
VAULTS = ["STACK-TECNOLOGICO", "SECDEV"]
SKIP_DIRS = {"scripts"}

def parse(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", t, re.S)
    fm, body = (m.group(1), t[m.end():]) if m else ("", t)
    ctx = ""
    cm = re.search(r"## Contexto en el mapa\s*\n(.*?)(\n## |\Z)", body, re.S)
    if cm:
        ctx = re.sub(r"\[\[([^\]|]+)(\|[^\]]+)?\]\]", r"\1", cm.group(1)).strip()
    return {
        "nivel": "dominar" if re.search(r"nivel:\s*dominar", fm) else "conocer",
        "estrella": bool(re.search(r"estrella:\s*true", fm)),
        "guia": bool(re.search(r"tipo:\s*guia", fm)),
        "relacionados": list(dict.fromkeys(re.findall(r"\[\[([^\]|]+)", fm)))[:8],
        "contexto": ctx[:400],
        "body": body if re.search(r"tipo:\s*guia", fm) else "",
        "propio": not m or ("Nodo del" not in body and "tipo: guia" not in fm),
    }

def build():
    inv = {}
    for v in VAULTS:
        vdir = os.path.join(ROOT, v)
        folders = sorted(d for d in os.listdir(vdir)
                         if os.path.isdir(os.path.join(vdir, d)) and d not in SKIP_DIRS and not d.startswith("."))
        inv[v] = {}
        for f in folders:
            notes = []
            for p in sorted(glob.glob(os.path.join(vdir, f, "*.md"))):
                d = parse(p); d["name"] = os.path.basename(p)[:-3]
                d["size"] = os.path.getsize(p)
                notes.append(d)
            inv[v][f] = notes
    return inv

if __name__ == "__main__":
    inv = build()
    for v, fs in inv.items():
        print(v, len(fs), "carpetas", sum(len(n) for n in fs.values()), "notas")
    json.dump(inv, open("/tmp/inventario.json", "w"), ensure_ascii=False)
