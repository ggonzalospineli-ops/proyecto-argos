# ENTITY_CATALOG.md — Fase 1

Catálogo completo de entidades evaluadas (lista del segundo/tercer bloque
del usuario). Para cada una: propósito, campos principales, relaciones,
lifecycle, ejemplo, y si entra al MVP (autoridad: "Practical MVP Boundary").

Leyenda: **MVP** = se implementa en Fase 9. **POST-MVP** = documentada acá,
no se implementa todavía (queda como diseño para v2+).

## MVP

### Project
- Propósito: proyecto raíz de ingeniería.
- Campos: id, name, description, status, created_at, updated_at.
- Relaciones: `has_many Systems`.
- Lifecycle: `ACTIVE → ARCHIVED`.
- Ejemplo real: `ARGOS 1` (único proyecto real hoy).

### System / Subsystem
- Propósito: agrupación funcional jerárquica dentro de un Project.
- Campos: id, project_id, parent_system_id (nullable, self-referencial),
  name, description, status, created_at, updated_at.
- Relaciones: `belongs_to Project`, `belongs_to System` (opcional, para
  subsistemas), `has_many Components`.
- Lifecycle: `ACTIVE → DEPRECATED`.
- Ejemplo: `Propulsion` [EJEMPLO — no confirmado en Argos real].

### Component
- Propósito: entidad de ingeniería versionable (pieza, módulo de software,
  conjunto).
- Campos: id, name, type (enum: `hardware`, `software`, `assembly`),
  description, parent_type (`system`/`component`), parent_id, status,
  current_revision_id, created_at, updated_at.
- Relaciones: `belongs_to System o Component (parent)`, `has_many Revisions`,
  `has_many Documents` (vía document_links), `has_many Dependencies`
  (depends_on / contains / compatible_with), `has_many BOM lines`.
- Lifecycle: `DRAFT → DESIGN → PROTOTYPE → TESTING → VALIDATED → RELEASED
  → DEPRECATED` (configurable, ver sección 20 del tercer bloque — el MVP
  usa este set fijo, no un motor de estados configurable).
- Ejemplo: `Motor Mount` [EJEMPLO].

### Revision
- Propósito: estado versionado inmutable de un Component.
- Campos: id, component_id, label (ej. "A", "B", "0.3"), status
  (`DRAFT`/`RELEASED`/`DEPRECATED`), description, change_summary, author,
  previous_revision_id, created_at.
- Relaciones: `belongs_to Component`, `has_many Artifacts`,
  `has_many Documents`, `has_many Tests` (a través de Build), referenciada
  por `BuildComponent`.
- Lifecycle: `DRAFT → RELEASED → DEPRECATED`. Inmutable una vez creada
  (nunca se edita el contenido de una Revision existente).
- Ejemplo: `Motor Mount Rev A` [EJEMPLO].

### Dependency
- Propósito: relación explícita entre dos Components.
- Campos: id, from_component_id, to_component_id, type (enum:
  `depends_on`, `contains`, `compatible_with`), notes, created_at.
- Relaciones: `belongs_to Component` (x2, from/to).
- Lifecycle: no versiona; se crea/borra.
- Ejemplo: `Motor Mount --depends_on--> Motor` [EJEMPLO].

### Document
- Propósito: contenido Markdown vinculado a una o más entidades.
- Campos: id, title, content (markdown), entity_type, entity_id, author,
  created_at, updated_at.
- Relaciones: polimórfica hacia System/Component/Revision/Build/Test.
- Lifecycle: `DRAFT → PUBLISHED`.
- Ejemplo: `Motor Mount — Design Notes` [EJEMPLO].

### Artifact
- Propósito: archivo binario (CAD, imagen, export) asociado a una Revision.
- Campos: id, revision_id, filename, file_type, size_bytes, checksum,
  storage_key, uploaded_by, uploaded_at.
- Relaciones: `belongs_to Revision`.
- Lifecycle: inmutable una vez subido (para reemplazar, se sube a una
  nueva Revision).
- Ejemplo: `motor-mount-rev-b.step` [EJEMPLO].

### BOMLine
- Propósito: relación cuantificada componente-padre / componente-hijo
  para construir la Bill of Materials.
- Campos: id, parent_component_id, child_component_id, quantity,
  child_revision_id (nullable = "usar current_revision").
- Relaciones: `belongs_to Component` (x2).
- Lifecycle: no versiona directamente; el BOM efectivo de una fecha se
  reconstruye vía las Revisions referenciadas en un Build.
- Ejemplo: `Airframe contains Motor Mount x4` [EJEMPLO].

### Build
- Propósito: configuración concreta de un prototipo/unidad física,
  referenciando revisiones exactas.
- Campos: id, project_id, code (ej. "ARGOS-01 Build #001"), description,
  status, created_at.
- Relaciones: `has_many BuildComponent` (component_id + revision_id
  congelados), `has_many Tests`.
- Lifecycle: `PLANNED → ASSEMBLED → TESTING → ARCHIVED`.
- Ejemplo: `ARGOS-01 Build #001` [EJEMPLO].

### Test
- Propósito: registro de una prueba sobre un Build/Component.
- Campos: id, name, target_component_id, build_id, description, result
  (enum `PASS`/`FAIL`/`INCONCLUSIVE`), notes, date, evidence (artifact
  refs), created_by.
- Relaciones: `belongs_to Build`, `belongs_to Component`.
- Lifecycle: `PLANNED → EXECUTED`.
- Ejemplo: `TEST-001 — Motor Mount vibration check` [EJEMPLO].

### User / Role
- Propósito: autenticación básica y permisos.
- Campos: id, email, name, role (`ADMIN`/`MEMBER`/`VIEWER`), created_at.
- Lifecycle: `ACTIVE → DISABLED`.

## POST-MVP (evaluadas, documentadas, no implementadas en Fase 9)

### Interface
- Propósito: contrato mecánico/eléctrico/software entre dos Components.
- Por qué queda fuera: el "Practical MVP Boundary" cubre relaciones
  simples (`depends_on`/`contains`/`compatible_with`); modelar interfaces
  con parámetros técnicos requeriría datos que hoy son `UNKNOWN`
  (ver `OPEN_QUESTIONS.md`). Se puede aproximar con `Dependency` +
  `Document` mientras tanto.

### Requirement
- Propósito: trazabilidad requisito → componente → test.
- Por qué queda fuera: no hay requisitos formales documentados de Argos
  todavía (sección 18, "Explicitly OUT OF SCOPE" del primer bloque no lo
  menciona, pero el MVP Boundary tampoco lo incluye en su lista de
  entidades mínimas). Candidato natural para v2 una vez que haya
  requisitos reales que trazar.

### Issue
- Propósito: problemas detectados durante builds/tests.
- Por qué queda fuera: el "Practical MVP Boundary" no lo incluye
  explícitamente. En el MVP, un problema se registra como `notes` dentro
  de `Test` o como `Document`. v2 lo formaliza como entidad con estado
  propio y relación a `ChangeRequest`.

### ChangeRequest
- Propósito: flujo formal de cambio (impact analysis → review → approval
  → nueva revisión).
- Por qué queda fuera: el primer bloque es explícito — "Do not implement
  ... automatic database modifications" y el MVP es de solo consulta para
  la IA; el flujo de cambio formal es post-MVP (ver `CHANGE_MANAGEMENT.md`,
  que lo diseña sin implementarlo).

### Decision (ADR)
- Propósito: registrar decisiones de diseño para que la IA no proponga de
  nuevo algo ya descartado.
- Por qué queda fuera: no bloquea el MVP; se puede representar como
  `Document` de tipo "decision" en el MVP usando la carpeta
  `/docs/decisions` (ver `DOCUMENTATION_ARCHITECTURE.md`) sin tabla
  dedicada, y promoverse a entidad propia en v2 si el volumen lo justifica.

### AIConversation / AIInsight
- Propósito: historial de conversaciones con el asistente de IA y
  hallazgos que genere.
- Por qué queda fuera de la Fase 9 mínima: el MVP solo necesita que el
  asistente responda con grounding y citas; persistir el historial de
  chat es una mejora de UX, no un requisito del "Practical MVP Boundary".
  Se documenta como extensión natural del `AIConversation` en
  `AI_ARCHITECTURE.md`.

### CADModel (como entidad separada de Artifact)
- Por qué queda fuera: el primer bloque es explícito — "support generic
  artifacts rather than building a complete CAD management system". CAD
  se modela como un `Artifact` con `file_type` en {STEP, STL, 3MF, ...},
  no como tabla propia.

## Resumen de alcance

| Entidad | MVP | Motivo si no |
|---|---|---|
| Project, System, Component, Revision, Dependency, Document, Artifact, BOMLine, Build, Test, User | ✅ | — |
| Interface | ❌ | requiere parámetros técnicos hoy UNKNOWN |
| Requirement | ❌ | no hay requisitos reales que trazar todavía |
| Issue | ❌ | cubierto por `notes` en Test / Document en MVP |
| ChangeRequest | ❌ | IA es read-only en MVP, no hay flujo de aprobación que orquestar |
| Decision | ❌ | cubierto por Document tipo "decision" |
| AIConversation/AIInsight | ❌ | mejora de UX post-MVP |
| CADModel | ❌ | cubierto por Artifact genérico |
