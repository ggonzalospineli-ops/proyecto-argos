# BOM_MODEL.md — Fase 2

## Principio

El BOM no es una tabla estática: se **deriva** de `bom_lines`
(`component_dependencies` con semántica `CONTAINS` + cantidad), igual que
pide el primer bloque del usuario ("BOM no debe ser simplemente una tabla
estática. Debe construirse a partir de las relaciones entre entidades").

## Estructura

```
bom_lines(parent_component_id, child_component_id, quantity, child_revision_id NULL)
```

- `child_revision_id = NULL` → al calcular el BOM efectivo, se resuelve
  contra `child_component.current_revision_id` en el momento de la
  consulta ("BOM de diseño actual").
- `child_revision_id` explícito → BOM congelado a una revisión concreta
  (usado cuando el BOM se calcula *dentro de un Build específico*, ver
  `BUILD_MODEL.md` — ahí en realidad se usa `build_components`, no
  `bom_lines`, para la congelación real).

## Reconstrucción recursiva de un BOM completo

```sql
WITH RECURSIVE bom AS (
  SELECT
    bl.parent_component_id,
    bl.child_component_id,
    bl.quantity,
    1 AS level
  FROM bom_lines bl
  WHERE bl.parent_component_id = :root_component_id

  UNION ALL

  SELECT
    bl.parent_component_id,
    bl.child_component_id,
    bom.quantity * bl.quantity,
    bom.level + 1
  FROM bom_lines bl
  JOIN bom ON bl.parent_component_id = bom.child_component_id
)
SELECT
  c.name,
  bom.quantity AS effective_quantity,
  bom.level,
  c.current_revision_id
FROM bom
JOIN components c ON c.id = bom.child_component_id
ORDER BY bom.level, c.name;
```

`effective_quantity` multiplica cantidades a través de niveles (ej. si
`Airframe contains Arm x4` y `Arm contains Motor Mount x1`, el Motor Mount
efectivo en el BOM completo de Airframe es 4).

## Protección contra ciclos

`bom_lines` no tiene protección de ciclos a nivel de constraint de
Postgres (los ciclos en jerarquías recursivas requieren trigger o chequeo
en aplicación). Regla de aplicación en Fase 9: antes de insertar una fila
en `bom_lines`, correr la misma CTE recursiva partiendo del
`child_component_id` propuesto y verificar que `parent_component_id` no
aparezca en el resultado (evita ciclo directo o indirecto). Se documenta
acá como requisito de la capa de servicio, no como trabajo de Fase 2.

## Ejemplo (ilustrativo, no real)

```
ARGOS 1
├── Airframe [EJEMPLO]
│   ├── Motor Mount ×4 [EJEMPLO]
│   └── Arm ×4 [EJEMPLO]
└── Propulsion [EJEMPLO]
    └── Motor ×4 [EJEMPLO]
```

Se representa como 3 filas en `bom_lines`
(`Airframe→Motor Mount qty=4`, `Airframe→Arm qty=4`,
`Propulsion→Motor qty=4`), no como una tabla plana escrita a mano.
