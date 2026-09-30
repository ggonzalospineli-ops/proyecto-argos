# PHASE_7_REPORT.md

**Objective**: Definir la primera capa de IA sobre el sistema (asistente
de ingeniería read-only, con grounding estricto).

**Completed**
- `AI_ARCHITECTURE.md` — flujo lineal Usuario→endpoint→structured
  queries + full-text search→LLM→respuesta con citas, sin multi-agente ni
  grafo dedicado, restricciones duras (read-only, no autónomo, grounding,
  fuera de alcance de contenido de armamento).
- `AI_CONTEXT_STRATEGY.md` — tres capas de contexto (structured/document/
  artifact metadata) siempre separadas y citadas, system prompt esqueleto,
  regla exacta de respuesta cuando no hay datos ("Information not defined
  in the current Argos knowledge base."), estrategia de source
  attribution.

**Not completed**
- AI Read-Only PoC funcional y source attribution en UI: se implementan
  en Fase 9 (estaban ya planificados ahí, no son documentos de Fase 7).

**Decisions**
- Sin router basado en LLM para clasificar la pregunta — heurística
  simple (keywords/nombres de entidad) para mantener el flujo lineal y
  barato, consistente con "keep the first implementation simple".
- El contexto nunca se rellena con conocimiento general del LLM cuando
  las queries estructuradas devuelven vacío — se fuerza la respuesta de
  "no definido" en vez de dejar que el modelo alucine plausibilidad.

**Unknowns**
- Proveedor de LLM final a usar (heredado de Fase 0/`OPEN_QUESTIONS.md`,
  sigue TO BE DEFINED) — el diseño es agnóstico de proveedor por env var,
  así que no bloquea el diseño, solo la configuración final en Fase 9.

**Risks**
- La heurística de clasificación de preguntas (sin LLM router) puede
  fallar en preguntas ambiguas o que crucen varias entidades a la vez;
  mitigación aceptada para el MVP: si la heurística no encuentra
  entidades relevantes, cae a full-text search general sobre
  `components`+`documents` antes de rendirse.
- Grounding estricto depende de que el system prompt se respete
  consistentemente por el LLM elegido — distintos proveedores pueden
  variar en qué tan bien seguyen esa instrucción; Fase 9 debe incluir al
  menos un test manual explícito de "pregunta sin respuesta en la base"
  antes de considerar el asistente confiable.

**Next phase**: Fase 8 — AI Impact Analysis.

**Recommended actions**
- Decidir proveedor de LLM antes de Fase 9 para no bloquear la
  implementación del endpoint.
