# BUILD_MODEL.md — Fase 2

## Principio

Un `Build` es la fotografía congelada de qué `Revision` de cada
`Component` compone un prototipo/unidad física concreta, en un momento
dado. Es la pieza que conecta el diseño digital versionado con la
realidad física (sección 9/15 del segundo/tercer bloque del usuario).

## Estructura

```
builds(id, project_id, code, description, status, created_at)
build_components(id, build_id, component_id, revision_id)
```

- `build_components.revision_id` es **siempre explícito** (a diferencia
  de `bom_lines.child_revision_id`, que puede ser NULL) — un Build no
  tiene ambigüedad de "usar la current": congela la revisión exacta usada
  en ese prototipo, incluso si el Component sigue evolucionando después.
- `code` es legible por humanos (`"ARGOS-01 Build #001"`), único por
  proyecto.

## Cómo se puebla un Build

1. Se elige el set de `Component`s relevantes (normalmente, expandiendo
   el BOM completo del proyecto o de un Component raíz vía la CTE de
   `BOM_MODEL.md`).
2. Para cada uno, se fija la `Revision` real usada (por defecto la
   `current_revision_id` del momento, pero puede ser una anterior si el
   build usó una pieza vieja en stock).
3. Se inserta una fila en `build_components` por cada par
   (component, revision).

## Estados

```
PLANNED ──► ASSEMBLED ──► TESTING ──► ARCHIVED
```

- **PLANNED**: se definió qué revisiones va a usar, todavía no se armó.
- **ASSEMBLED**: el prototipo físico existe.
- **TESTING**: en campaña de pruebas activa.
- **ARCHIVED**: build retirado/histórico, se conserva por trazabilidad.

## Consultas típicas

**Configuración completa de un Build:**
```sql
SELECT c.name AS component, r.label AS revision
FROM build_components bc
JOIN components c ON c.id = bc.component_id
JOIN revisions r ON r.id = bc.revision_id
WHERE bc.build_id = :build_id
ORDER BY c.name;
```

**Todos los Builds que usaron una Revision específica** (para impact
analysis — ver `IMPACT_ANALYSIS.md`):
```sql
SELECT b.code FROM build_components bc
JOIN builds b ON b.id = bc.build_id
WHERE bc.revision_id = :revision_id;
```

## Relación con Tests

`tests.build_id` (nullable) ata un test a un build concreto;
`tests.target_component_id` (NOT NULL) siempre indica qué componente se
está probando, esté o no atado a un build. Esto permite tanto "tests de
un build completo" como "tests de un componente aislado en banco de
pruebas" sin forzar un build ficticio.

## Ejemplo (ilustrativo, no real)

```
ARGOS-01 Build #001 [EJEMPLO]
  Airframe   → Rev B
  Motor Mount → Rev A
  Motor      → Rev A
```
