# BUILD_WORKFLOW.md — Fase 6

## Flujo

```
Design (Components en RELEASED con Revisions definidas)
  → Build (se crea, status=PLANNED, se eligen las Revisions exactas — ver BUILD_MODEL.md)
  → [ensamblado físico fuera de la plataforma]
  → Build.status = ASSEMBLED
  → Test (uno o más Tests contra el Build, status=TESTING)
  → Result (PASS/FAIL/INCONCLUSIVE registrado por Test)
  → Issue (si FAIL o INCONCLUSIVE relevante — en el MVP, se documenta en
           tests.notes o como Document con templates/issue.md, no como
           entidad Issue dedicada — ver ENTITY_CATALOG.md)
  → Change (si el issue requiere rediseño — ver CHANGE_MANAGEMENT.md,
            genera una nueva Revision del Component afectado)
```

Un Build puede pasar a `ARCHIVED` en cualquier punto una vez que deja de
ser relevante operativamente (ej. fue reemplazado por un Build más nuevo),
sin perder su historial.

## Responsabilidades por estado de Build

| Estado | Qué implica | Quién lo cambia |
|---|---|---|
| PLANNED | Se definieron las Revisions a usar, no existe físicamente | quien planifica el build |
| ASSEMBLED | El prototipo físico existe | quien lo arma, tras confirmarlo |
| TESTING | Hay una campaña de pruebas activa | se mantiene mientras haya Tests pendientes/en curso |
| ARCHIVED | Ya no es el build de referencia activo | manual, cuando se reemplaza |

## Relación Build ↔ Test ↔ Component

Ver `BUILD_MODEL.md` para el detalle de tablas. En resumen: un `Test`
siempre apunta a un `target_component_id`, y opcionalmente a un
`build_id` — esto permite tanto "testeamos el Motor Mount dentro del
Build #001" como "testeamos el Motor Mount aislado en banco, sin build
asociado".
