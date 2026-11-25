---
titulo: "MCP security"
categoria:
  - "Seguridad en IA, LLM y agentes"
tags:
  - "secdev"
  - "nivel-conocer"
  - "seguridad-en-ia-llm-y-agentes"
nivel: conocer
estrella: false
relacionado_con:
  - "[[AI supply chain]]"
  - "[[Agent security]]"
  - "[[Content filtering]]"
  - "[[Context window leakage]]"
  - "[[Embedding security]]"
  - "[[Function calling security]]"
  - "[[Guardrails (LLM)]]"
  - "[[Herramientas para agentes]]"
  - "[[Model provenance]]"
  - "[[Model signing]]"
---

# MCP security

> Nodo del mapa **SECDEV** — seguridad informática aplicada al desarrollo de software.

## Contexto en el mapa

**Agentes y herramientas:** [[Agent security]], [[Function calling security]], [[MCP security]], [[Herramientas para agentes]], [[Validación de salida del modelo]], [[Guardrails (LLM)]], [[Content filtering]], [[Red teaming LLM]], [[AI supply chain]], [[Model provenance]], [[Model signing]], [[Vector database security]], [[Embedding security]], [[Context window leakage]], [[PII en prompts]].

## Relaciones

- [[AI supply chain]]
- [[Agent security]]
- [[Content filtering]]
- [[Context window leakage]]
- [[Embedding security]]
- [[Function calling security]]
- [[Guardrails (LLM)]]
- [[Herramientas para agentes]]
- [[Model provenance]]
- [[Model signing]]

## Cómo se aplica

Describe aquí: para qué sirve, qué hace y cómo funciona en tu propio proyecto.

## Caso concreto: AGENT BROWSER (es un tema de MCP, no una nota aparte)

Un **AGENT BROWSER** es el navegador que un agente de IA controla para leer páginas, hacer clic y rellenar formularios por él. Dentro de MCP es un tema de esta nota porque amplía la superficie de ataque del protocolo: una página maliciosa puede inyectar instrucciones indirectas, el agente puede filtrar datos del contexto y un tool mal definido puede actuar con permisos excesivos. Defensas: permitir solo dominios confiables, tratar el contenido web como datos no confiables, validar cada acción del agente, aplicar menor privilegio a las herramientas y pedir confirmación humana para operaciones sensibles.

## Mis notas

Añade ejemplos, comandos, errores comunes y experiencias reales.
