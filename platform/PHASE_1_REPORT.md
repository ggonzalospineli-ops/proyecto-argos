# PHASE_1_REPORT.md

**Objective**: Definir el modelo conceptual de Argos como sistema de
ingeniería (jerarquía, catálogo de entidades, relaciones, diagrama).

**Completed**
- `ARGOS_SYSTEM_MODEL.md` — jerarquía `Project → System → Subsystem →
  Component → Revision → Artifact`, con `Component` autorreferente para
  cubrir el caso "Assembly" sin entidad nueva.
- `ENTITY_CATALOG.md` — 11 entidades evaluadas para MVP (Project, System,
  Component, Revision, Dependency, Document, Artifact, BOMLine, Build,
  Test, User) y 7 evaluadas y explícitamente diferidas a post-MVP
  (Interface, Requirement, Issue, ChangeRequest, Decision, AIConversation/
  AIInsight, CADModel).
- `RELATIONSHIP_MODEL.md` — relaciones estructurales, de componente
  (depends_on/contains/compatible_with), documentales, y de build/test,
  con las cadenas de trazabilidad que responden las preguntas de ejemplo
  del usuario.
- `ARGOS_SYSTEM_MODEL_DIAGRAM.md` — diagrama Mermaid del modelo completo,
  usando exclusivamente datos marcados `[EJEMPLO]`.

**Not completed**
- Ninguno de los entregables de Fase 1 quedó pendiente.

**Decisions**
- "Assembly" no es una tabla separada: se modela como `Component` con
  hijos vía `BOMLine` (`contains`). Reduce una entidad sin perder
  capacidad expresiva.
- El alcance de entidades del MVP sigue estrictamente el "Practical MVP
  Boundary" del usuario, no las listas más amplias de los otros dos
  bloques — esas se documentan pero no se construyen todavía.
- Lifecycle de `Component` fijo (DRAFT→DESIGN→PROTOTYPE→TESTING→
  VALIDATED→RELEASED→DEPRECATED), no configurable en el MVP, para no
  sobre-construir un motor de estados sin caso de uso real todavía.

**Unknowns** (heredados de Fase 0, no resueltos acá — son decisiones de
producto/negocio, no de modelado)
- Si `SENTINEL-1` es un Project separado o un System dentro de `ARGOS 1`.
- Si el pipeline de `vision/` se integra al modelo como Component
  versionado o queda como repo independiente.

**Risks**
- Sin datos reales de componentes, el modelo solo se puede validar con
  ejemplos ficticios — el riesgo real (¿el modelo sirve para el Argos
  real?) no se puede cerrar hasta Fase 10 con datos reales del usuario.
- La jerarquía recursiva de `Component` (para Assembly) requiere queries
  recursivas (CTE) para reconstruir un BOM completo — viable en
  PostgreSQL pero hay que implementarlo con cuidado en Fase 9 (evitar
  ciclos).

**Next phase**: Fase 2 — Modelo de datos (schema PostgreSQL, ERD,
versionamiento, BOM, builds).

**Recommended actions**
- Cuando el usuario tenga el primer componente real de Argos, usarlo como
  caso de prueba antes de seguir agregando features al modelo.
