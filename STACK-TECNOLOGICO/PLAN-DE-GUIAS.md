---
titulo: Plan de guías — Mapa Tecnológico
tags: [mapa-tecnologico, guia-completa, plan]
tipo: indice
estado: oleada-1-completa
actualizado: 2026-11-24
---

# Plan de guías — de índice a "guía de todo" 📚

> Objetivo: que cada nodo del mapa deje de ser un stub y se convierta en una **guía de estudio utilizable**: instalación, comandos, ejemplos, flujo de trabajo, errores comunes y relaciones.

## 1. Realidad y estrategia

El mapa v2.6 tiene **1322 nodos** (872 originales + ~450 del plan de estudios). Escribir 1322 guías profundas de una vez es imposible de hacer bien (y de leer). Por eso se trabaja por **oleadas**, priorizando los ⭐ núcleo.

> **Estado actual:** fase de mapa **cerrada**; las guías detalladas están **en pausa** (las 14 del núcleo quedan como plantilla) y se harán una por una más adelante.

| Oleada | Contenido | Estado |
|---|---|---|
| **0** | Infraestructura del vault: MOC, grafo, README, PDF | ✅ cerrada (v2.6) |
| **1** | ⭐ Núcleo imprescindible (14 notas) | ✅ cerrada (14/14) |
| **2** | Nodos puente y herramientas del día a día | 🔄 siguiente |
| **3** | Resto por categoría (AWS, redes, IA, seguridad, testing…) | ⏳ pendiente |
| **4** | Especialización AppSec (rama nueva, cuando toque) | ⏳ pendiente |

> No hace falta dominar las 872 notas. El criterio es: **⭐ dominar → conocer → especialidad**. Ver [[SOFTWARE-ENGINEERING]] y [[README]].

## 2. Plantilla de una guía completa

Toda nota convertida mantiene su `frontmatter` original y agrega:

```yaml
tags: [..., guia-completa]
tipo: guia
estado: completa        # o "en-progreso"
actualizado: 2026-11-24
```

Estructura estándar de contenido (adaptar según el tema):

1. **Mentalidad** — qué es, qué NO es, por qué existe (y una frase para entrevista).
2. **Instalación / primeros pasos** — comandos por Linux, macOS y Windows.
3. **Cheat sheet** — tabla de comandos/conceptos con la explicación al lado.
4. **Flujo diario / ejemplo mínimo** — el caso práctico que se usa siempre.
5. **Profundidad** — internals, arquitectura, patrones, comparativas.
6. **Configuración avanzada** — opciones, ajuste, rendimiento.
7. **Errores comunes y troubleshooting** — síntoma → causa → solución.
8. **Seguridad / buenas prácticas** — checklist (especialmente útil para AppSec).
9. **Ejercicios** — 5–7 tareas para fijar el conocimiento.
10. **Relaciones** — wikilinks a los nodos vecinos existentes.

Reglas:

- Los enlaces de doble corchete deben apuntar **a notas que existen** (validar al final).
- Se conserva `relacionado_con` del frontmatter aunque la guía agregue más links en el cuerpo.
- Las guías se escriben **directamente en la nota**; el generador las respeta (tiene lógica de preservación).
- Idioma: español, tono práctico, comandos copiables.

## 3. Oleada 1 — ⭐ Núcleo imprescindible

- [x] [[Git]] — modelos, comandos, flujos, conflictos, reflog, emergencias.
- [x] [[Docker]] — instalación, comandos, Dockerfile, Compose, redes, volúmenes, seguridad.
- [x] [[SQL]] — consultas, joins, índices, transacciones, explain, normalización.
- [x] [[PostgreSQL]] — instalación, psql, roles, backups, Índices, WAL, pgvector.
- [x] [[HTTP]] — métodos, códigos, headers, caché, sesiones, REST.
- [x] [[HTTPS - TLS]] — certificados, handshake, cipher suites, HSTS, Let's Encrypt.
- [x] [[Python]] — entornos, pip/uv, sintaxis, OOP, async, testing, empaquetado.
- [x] [[GitHub Actions]] — workflows, jobs, secrets, matrices, caching, OIDC.
- [x] [[RDS]] — crear instancia, conexión, snapshots, IAM, VPC, costos.
- [x] [[DTO]] — validación, Pydantic, mapeo, capas, ejemplos.
- [x] [[Middleware]] — orden, CORS, auth, logging, manejo de errores.
- [x] [[Logs estructurados]] — JSON logs, correlation ID, niveles, agregación.
- [x] [[Prompt engineering]] — patrones, system prompts, few-shot, evaluación.
- [x] [[MCP (Model Context Protocol)]] — arquitectura, servidores, tools, recursos, seguridad.

> Nota: el núcleo también menciona **Linux**, que en el mapa se cubre a través de [[Kernel]], [[Bash - Shell]], [[systemctl - journalctl]], [[POST - BIOS - UEFI]] y [[Usuario root - UID - GID - sudo]]. Si querés una guía `Linux.md` propia, se agrega como nodo nuevo.

## 4. Oleada 2 — próximos candidatos (nodos puente y uso diario)

- [[Docker Compose]] · [[Kubernetes]] · AWS CLI · [[IAM]] · [[S3 (bucket)]] · [[SQS]] · [[SNS]] · [[CloudWatch]]
- [[Redis]] · [[RabbitMQ]] · [[Kafka]] · [[EventBridge]]
- [[GitHub]] · [[GitFlow]] · [[Husky]] · [[Conventional Commits]] · [[.gitignore]]
- [[nginx]] · [[Traefik]] · [[Route 53]] · [[Cloudflare]] · [[TCP-IP]] · [[DNS]]
- [[JWT]] · [[OAuth 2.0]] · [[OWASP Top 10]] · [[Gestión de secretos]]
- [[OpenCode]] · [[Claude Code]] · [[Orca.dev]] · [[Worktrees paralelos]]

## 5. Cómo validar

Después de cada tanda:

```bash
# Regenerar stubs sin borrar las guías ya escritas
python3 /home/payan/Descargas/stack_enginnering/generar_vault.py

# Contar guías completas
grep -rl 'tipo: guia' "/home/payan/Documentos/Obsidian Vault/STACK-TECNOLOGICO" | wc -l

# Verificar que no haya wikilinks rotos
python3 - <<'PY'
import os, re
root = "/home/payan/Documentos/Obsidian Vault/STACK-TECNOLOGICO"
notas = set()
for d, _, fs in os.walk(root):
    for f in fs:
        if f.endswith(".md"):
            notas.add(os.path.splitext(f)[0])
rotos = set()
for d, _, fs in os.walk(root):
    for f in fs:
        if f.endswith(".md"):
            for t in re.findall(r"\[\[([^\]]+)\]\]", open(os.path.join(d, f), encoding="utf-8").read()):
                if t not in notas:
                    rotos.add(t)
print("wikilinks rotos:", len(rotos), sorted(rotos)[:20])
PY
```

## 6. Estado global

| Métrica | Valor |
|---|---|
| Notas totales | 872 + MOC + grafo + README + este plan |
| Guías completas | **14** (todo el núcleo ⭐) |
| Wikilinks | ver validación (objetivo: **0 rotos**) |
| PDF consolidado | `Stack_Tecnologico_v2.6.pdf` (edición explicativa: cada carpeta, tema y tecnología responde para qué sirve, qué hace y cómo funciona) |
