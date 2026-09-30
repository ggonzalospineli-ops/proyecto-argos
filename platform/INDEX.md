# INDEX.md — Argos Engineering Platform

Punto de entrada único a todo el trabajo de `platform/`. Fases 0-10
completas, siguiendo el proceso de gates definido por el usuario. **No se
tocó `vision/` ni `empresaquevendearmasproyecto-2028.html` en ningún
momento** — ambos permanecen exactamente como estaban.

## Estado real, en una frase

**Modelo de datos y diseño: completo y consistente. Código: compila y
buildea limpio, pero no está probado contra una base de datos real ni
cargado con datos reales de Argos — falta la UI de escritura y una
instancia de Postgres para el primer uso real.**

## Fase 0 — Reconocimiento
| Archivo | Qué es |
|---|---|
| [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) | Qué es Argos según el material existente, KNOWN/UNKNOWN/TBD |
| [CURRENT_ARCHITECTURE.md](CURRENT_ARCHITECTURE.md) | Mapa de arquitectura real (solo `vision/` tiene código) |
| [CURRENT_COMPONENTS.md](CURRENT_COMPONENTS.md) | Inventario de todo lo mencionado, clasificado |
| [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) | Preguntas abiertas + límites explícitos de alcance |

## Fase 1 — Modelo conceptual
| Archivo | Qué es |
|---|---|
| [ARGOS_SYSTEM_MODEL.md](ARGOS_SYSTEM_MODEL.md) | Jerarquía Project→System→Subsystem→Component→Revision→Artifact |
| [ENTITY_CATALOG.md](ENTITY_CATALOG.md) | 11 entidades MVP + 7 evaluadas y diferidas post-MVP |
| [RELATIONSHIP_MODEL.md](RELATIONSHIP_MODEL.md) | depends_on/contains/compatible_with, cadenas de trazabilidad |
| [ARGOS_SYSTEM_MODEL_DIAGRAM.md](ARGOS_SYSTEM_MODEL_DIAGRAM.md) | Diagrama Mermaid (datos ilustrativos) |
| [PHASE_1_REPORT.md](PHASE_1_REPORT.md) | Reporte de gate |

## Fase 2 — Modelo de datos
| Archivo | Qué es |
|---|---|
| [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) | Schema PostgreSQL completo + ERD Mermaid |
| [VERSIONING_MODEL.md](VERSIONING_MODEL.md) | Inmutabilidad de Revisions, DRAFT→RELEASED→DEPRECATED |
| [BOM_MODEL.md](BOM_MODEL.md) | BOM derivado (CTE recursiva), no tabla estática |
| [BUILD_MODEL.md](BUILD_MODEL.md) | Congelamiento de (component, revision) por build |
| [PHASE_2_REPORT.md](PHASE_2_REPORT.md) | Reporte de gate |

## Fase 3 — Documentación / Knowledge Base
| Archivo | Qué es |
|---|---|
| [DOCUMENTATION_ARCHITECTURE.md](DOCUMENTATION_ARCHITECTURE.md) | `/docs` como espejo, DB como fuente de verdad |
| [DOCUMENT_LINKING.md](DOCUMENT_LINKING.md) | FK polimórfica entity_type+entity_id |
| [KNOWLEDGE_MODEL.md](KNOWLEDGE_MODEL.md) | Qué dato va estructurado vs. documento vs. artifact |
| [templates/](templates/) | 8 templates Markdown (component, system, requirement, test, issue, decision, change-request, build) |
| [PHASE_3_REPORT.md](PHASE_3_REPORT.md) | Reporte de gate |

## Fase 4 — CAD / Artifacts
| Archivo | Qué es |
|---|---|
| [ARTIFACT_MODEL.md](ARTIFACT_MODEL.md) | Campos, interfaz `ArtifactStorage` abstracta |
| [CAD_WORKFLOW.md](CAD_WORKFLOW.md) | Flujo CAD→Export→Revision→Upload→Review |
| [CAD_FORMAT_MATRIX.md](CAD_FORMAT_MATRIX.md) | STL/3MF priorizados para preview |
| [PHASE_4_REPORT.md](PHASE_4_REPORT.md) | Reporte de gate (3D Viewer diferido a Fase 9) |

## Fase 5 — Versionamiento / Change Management
| Archivo | Qué es |
|---|---|
| [CHANGE_MANAGEMENT.md](CHANGE_MANAGEMENT.md) | Flujo CR→Impact→Review→Revision (manual en MVP) |
| [AUDIT_MODEL.md](AUDIT_MODEL.md) | Qué se audita hoy sin tabla dedicada, diseño de `audit_log` futuro |
| [PHASE_5_REPORT.md](PHASE_5_REPORT.md) | Reporte de gate |

## Fase 6 — Builds, prototipos y testing
| Archivo | Qué es |
|---|---|
| [BUILD_WORKFLOW.md](BUILD_WORKFLOW.md) | Design→Build→Test→Result→Issue→Change |
| [TRACEABILITY_EXAMPLE.md](TRACEABILITY_EXAMPLE.md) | Ejemplo end-to-end completo (datos 100% ficticios, marcados) |
| [PHASE_6_REPORT.md](PHASE_6_REPORT.md) | Reporte de gate |

## Fase 7 — AI Engineering Assistant
| Archivo | Qué es |
|---|---|
| [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) | Flujo lineal sin multi-agente, restricciones duras (read-only) |
| [AI_CONTEXT_STRATEGY.md](AI_CONTEXT_STRATEGY.md) | 3 capas de contexto, grounding estricto, source attribution |
| [PHASE_7_REPORT.md](PHASE_7_REPORT.md) | Reporte de gate |

## Fase 8 — AI Impact Analysis (diseño, no implementado en MVP)
| Archivo | Qué es |
|---|---|
| [IMPACT_ANALYSIS.md](IMPACT_ANALYSIS.md) | Cálculo de impacto vía SQL recursivo, explícitamente post-MVP |
| [PHASE_8_REPORT.md](PHASE_8_REPORT.md) | Reporte de gate |

## Fase 9 — Plataforma MVP (código real)
| Ruta | Qué es |
|---|---|
| [app/](app/) | App Next.js 14 + TypeScript + Prisma completa — ver `app/README.md` |
| [PHASE_9_REPORT.md](PHASE_9_REPORT.md) | Qué se implementó, qué no (UI de escritura, driver S3, 3MF), verificación de build |

**Funcional (compila/buildea)**: schema Prisma, auth, storage abstraído,
búsqueda full-text, AI assistant read-only, páginas de lectura (Dashboard,
System Explorer, Component/Revision/Build Page, Search, AI chat), 3D
viewer PoC (STL), seed de datos de ejemplo.

**Diseñado pero NO implementado en código**: UI de creación/edición
(Components, Artifacts, Builds, Tests, Documents), driver de storage S3,
preview 3MF, protección de rutas por sesión a nivel de página,
`audit_log`, `ChangeRequest`/`Issue`/`Requirement`/`Decision` como
entidades propias, impact analysis automatizado.

## Fase 10 — Validación con Argos real
| Archivo | Qué es |
|---|---|
| [MIGRATION_PLAN.md](MIGRATION_PLAN.md) | Qué datos reales existen (casi ninguno), qué falta pedir al usuario |
| [MVP_VALIDATION.md](MVP_VALIDATION.md) | Reporte honesto: qué se pudo probar (build) vs. qué quedó bloqueado (runtime, datos reales) |
| [PHASE_10_REPORT.md](PHASE_10_REPORT.md) | Reporte de gate final |

## Qué haría falta para que esto sea usable por el equipo mañana

1. Una instancia de PostgreSQL + `prisma migrate dev` + `npm run seed`.
2. UI de escritura (crear Component/Artifact/Build/Test) — hoy no existe.
3. Guard de sesión por página.
4. Los insumos reales listados en `MIGRATION_PLAN.md` (inventario,
   CAD, decisión sobre `vision/`).

## Límite de alcance que se mantuvo durante todo el trabajo

No se generó, en ningún documento ni en el código, contenido técnico de
sistemas de guiado de misiles, seekers, o armamento (la "Fase 3" del
roadmap de negocio en el HTML) — ver la nota de alcance en
[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).
