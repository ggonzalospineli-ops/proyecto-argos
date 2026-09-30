# PHASE_8_REPORT.md

**Objective**: Definir cómo se calcularía impact analysis a partir de un
cambio propuesto.

**Completed**
- `IMPACT_ANALYSIS.md` — diseño completo (dependencias directas/
  indirectas vía clausura transitiva SQL, builds/tests/documentos
  afectados, flujo de Change Proposal), explícitamente marcado como
  POST-MVP y no implementado en Fase 9.

**Not completed**
- Implementación funcional — intencional, fuera del "Practical MVP
  Boundary" del usuario.

**Decisions**
- El cálculo de impacto es SQL determinístico (CTE recursiva sobre
  `component_dependencies`), no un LLM "adivinando" — la IA solo lo
  presenta en lenguaje natural una vez implementado, para no introducir
  alucinación en algo que debe ser exacto.
- Se documenta ahora (en vez de posponerlo sin diseño) porque no requiere
  cambios al schema ya definido en Fase 2 — es pura lógica de consulta
  sobre datos existentes, bajo costo de mantener el diseño listo.

**Unknowns**
- Ninguno nuevo — depende de que haya suficiente `component_dependencies`
  real cargada para ser útil, lo cual depende de datos reales (Fase 10).

**Risks**
- Ninguno nuevo para el MVP, dado que no se implementa. Riesgo diferido:
  cuando se implemente, la clausura transitiva sin límite de profundidad
  podría ser costosa en un grafo muy denso — se puede acotar con `depth <
  N` en la CTE si hace falta.

**Next phase**: Fase 9 — Plataforma MVP (implementación de código real).

**Recommended actions**
- Ninguna inmediata — retomar este documento cuando haya volumen real de
  dependencias cargadas y el equipo sienta la necesidad de esto en la
  práctica.
