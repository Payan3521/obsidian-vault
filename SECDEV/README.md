---
titulo: README del vault SECDEV
tags: [secdev, README]
---

# README — Mapa SECDEV

Este vault se generó desde `secdev.md` con `generar_secdev.py`. Es el mapa de tu especialización:
**seguridad informática aplicada al desarrollo de software**.

## Cómo usarlo

1. Abre **[[SECDEV]]** — es el índice maestro.
2. Empezá por los nodos **⭐ Núcleo de la especialización**.
3. Cada nota tiene:
   - `categoria`: todas las categorías donde aparece el tema.
   - `nivel`: `dominar` (⭐) o `conocer`.
   - `relacionado_con`: nodos con los que comparte línea/contexto + relaciones manuales.
   - `## Contexto en el mapa`: la frase original de la que salió el nodo.
   - `## Cómo se aplica` y `## Mis notas`: espacio para tu experiencia.
4. **[[grafo]]** contiene los diagramas Mermaid del mapa.
5. **[[PLAN-DE-GUIAS]]** explica cómo convertir cada nota en una guía completa por oleadas.
   Las notas con `tipo: guia` se preservan automáticamente al regenerar.

## Los 3 niveles

| Nivel | Significado |
|---|---|
| `dominar` | Lo defenderías en una entrevista de AppSec (⭐). |
| `conocer` | Sabes qué es y cuándo se usa, sin configurarlo de memoria. |
| `especialidad` | Tu barra vertical: esta carpeta entera. |

> Nadie domina las 1173 notas. Esto es un mapa de especialización, no un examen.

## Diferencia con STACK-TECNOLOGICO

- `STACK-TECNOLOGICO/` cubre **toda la ingeniería de software** (casi imposible de dominar completa).
- `SECDEV/` cubre **solo seguridad aplicada al software**: cómo construir, desplegar y operar sin abrir puertas de entrada.
- No hay duplicado de contenido: los nodos de `SECDEV` viven en su propia carpeta y se enlazan entre sí.

## Estructura final del vault

- `SECDEV/` — 29 categorías, `SECDEV.md`, `grafo.md`, `PLAN-DE-GUIAS.md` y notas.
- `STACK-TECNOLOGICO/` — el mapa general; queda intacto.
- `proyectos/` — queda aparte e intacto.

> Al regenerar, el script preserva automáticamente **todo** lo que no generó él (guías completas, apuntes propios y adjuntos).
