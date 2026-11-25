---
titulo: Plan de guías — SECDEV
tags: [secdev, guia-completa, plan]
---

# Plan de guías — de índice a guía de seguridad 🛡️

> Objetivo: que cada nodo de `SECDEV/` deje de ser un stub y se convierta en una guía de estudio
> utilizable: instalación, comandos, configuración segura, errores comunes y ejercicios.

El mapa SECDEV tiene **1073 nodos**. Escribir 1073 guías profundas de una vez
no es posible hacerlo bien. Se trabaja por **oleadas**, priorizando los 27 nodos ⭐ del núcleo.

> **Estado actual:** fase de mapa **cerrada**; las guías detalladas están **en pausa** y se harán una por una.

## Oleadas sugeridas

| Oleada | Categorías | Estado |
|---|---|---|
| 1 | Fundamentos, ciclo de vida, modelado de amenazas | pendiente |
| 2 | OWASP, autenticación, autorización | pendiente |
| 3 | Criptografía, secretos, APIs, datos | pendiente |
| 4 | Cloud, contenedores, IaC, CI/CD | pendiente |
| 5 | SAST/DAST/SCA, monitoreo, incidentes | pendiente |
| 6 | Legal, gobierno, IA y agentes | pendiente |

## Plantilla de una guía completa

```md
---
titulo: Nombre del tema
tags: [secdev, guia-completa]
tipo: guia
nivel: dominar
---

# Nombre del tema

## Para qué sirve
## Qué hace
## Cómo funciona
## Configuración segura paso a paso
## Comandos y ejemplos
## Errores comunes
## Cómo se verifica que quedó seguro
## Relaciones
```

> Las notas con `tipo: guia` se escriben directamente en la nota y el generador las respeta.

## Regenerar stubs sin borrar guías

```bash
python3 /home/payan/Descargas/stack_enginnering/generar_secdev.py
```

## Estado

| Métrica | Valor |
|---|---|
| Nodos del mapa | **1073** |
| Categorías | **28** |
| Núcleo ⭐ | **27** |
| Guías completas | **0** (pendientes) |
