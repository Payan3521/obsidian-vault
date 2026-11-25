---
titulo: README del vault
tags: [mapa-tecnologico, README]
---

# README — Stack Tecnológico v2.6

Este vault se generó desde `stack-tecnologico.md`.

## Cómo usarlo

1. Abre **[[SOFTWARE-ENGINEERING]]** — es el índice maestro.
2. Empieza por la sección **⭐ Núcleo imprescindible**.
3. Cada nota tiene:
   - `categoria`: todas las categorías donde aparece el nodo.
   - `nivel`: `dominar` (⭐) o `conocer`.
   - `relacionado_con`: nodos con los que comparte categoría + relaciones manuales.
   - `## Contexto en el mapa`: la frase original de la que salió el nodo.
   - `## Mis notas`: espacio para tu experiencia.
4. **[[grafo]]** contiene los diagramas Mermaid.
5. El PDF consolidado está en esta carpeta: `Super_Stack_Tecnologico_Ingenieria_Software.pdf` (edición explicativa: cada carpeta, tema y tecnología responde para qué sirve, qué hace y cómo funciona).
6. **[[PLAN-DE-GUIAS]]** explica cómo convertir cada nota en una guía completa por oleadas.
   Las notas con `tipo: guia` se preservan automáticamente al regenerar el vault.

## Los 3 niveles

| Nivel | Significado |
|---|---|
| `dominar` | Lo usas cada semana y lo defenderías en una entrevista (⭐). |
| `conocer` | Sabes qué es y cuándo se usa, sin configurarlo de memoria. |
| `especialidad` | Tu barra vertical (aquí: seguridad de software / AppSec). |

> Recordatorio: nadie domina las 1416 notas. Esto es un mapa, no un examen.

## Estructura final del vault

- `STACK-TECNOLOGICO/` — el mapa completo, las guías y tus apuntes integrados:
  - `arquitectura/`, `documentacion/` — tus carpetas originales, movidas aquí sin perder contenido.
  - 50 categorías generadas, `SOFTWARE-ENGINEERING.md`, `grafo.md`, `PLAN-DE-GUIAS.md` y el PDF.
- `proyectos/` — queda aparte e intacto.

> Al regenerar, el script preserva automáticamente **todo** lo que no generó él (guías completas, apuntes propios y adjuntos). Puedes volver a generar el mapa sin miedo a perder trabajo.
