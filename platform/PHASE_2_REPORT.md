# PHASE_2_REPORT.md

**Objective**: Convertir el modelo conceptual de Fase 1 en una estructura
de datos implementable (schema PostgreSQL, ERD, versionamiento, BOM,
builds).

**Completed**
- `DATABASE_SCHEMA.md` — 11 tablas MVP (users, projects, systems,
  components, revisions, artifacts, documents, component_dependencies,
  bom_lines, builds, build_components, tests — 12 en total), enums,
  índices, triggers de `search_vector`, ERD Mermaid.
- `VERSIONING_MODEL.md` — inmutabilidad de Revision garantizada a nivel de
  schema (sin `updated_at` en `revisions`), máquina de estados
  DRAFT→RELEASED→DEPRECATED, reconstrucción de historial vía CTE
  recursiva.
- `BOM_MODEL.md` — BOM derivado (no tabla estática), CTE recursiva con
  cantidades efectivas multiplicadas por nivel, nota sobre protección de
  ciclos a nivel de aplicación.
- `BUILD_MODEL.md` — `build_components` congela `(component_id,
  revision_id)` explícitamente, estados PLANNED→ASSEMBLED→TESTING→
  ARCHIVED, queries de configuración de build y de impacto por revisión.

**Not completed**
- Ninguno de los entregables de Fase 2 quedó pendiente.

**Decisions**
- `bom_lines` se mantiene como tabla separada de `component_dependencies`
  en vez de reusar `type='CONTAINS'` de esa tabla, porque BOM necesita
  `quantity` y `child_revision_id`, que no aplican a `depends_on`/
  `compatible_with`. Es una pequeña duplicación de concepto a cambio de
  no forzar columnas nullable específicas de BOM en la tabla genérica de
  dependencias.
- Búsqueda semántica (pgvector) explícitamente fuera del schema del MVP —
  columna de embeddings se agrega en una migración futura si se decide
  usarla.
- `documents.entity_id` es una FK polimórfica sin constraint de integridad
  referencial a nivel de Postgres (se valida en la capa de aplicación) —
  trade-off estándar para polimorfismo sin tabla de unión extra.

**Unknowns**
- Ninguno nuevo — los unknowns de negocio/datos reales siguen siendo los
  de Fase 0/1, no bloquean el schema.

**Risks**
- La FK polimórfica de `documents` puede acumular filas huérfanas si se
  borra una entidad referenciada sin borrar sus documentos — Fase 9 debe
  usar transacciones o `ON DELETE` en cascada manejado en la capa de
  servicio (Prisma no soporta FK polimórfica nativa, se implementa con
  validación en el resolver).
- El chequeo de ciclos en `bom_lines` no está en la base de datos —
  depende de disciplina en la capa de aplicación (Fase 9); si se accede a
  la DB directamente sin pasar por esa capa, se pueden crear ciclos.

**Next phase**: Fase 3 — Documentación y Knowledge Base.

**Recommended actions**
- Al implementar Fase 9, escribir un test de integración específico para
  el chequeo de ciclos de `bom_lines` antes de dar por buena esa función.
