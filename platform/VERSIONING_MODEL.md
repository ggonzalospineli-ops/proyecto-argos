# VERSIONING_MODEL.md — Fase 2

## Principio

Una `Revision` es inmutable una vez creada, salvo su `status`. "Editar"
una pieza siempre significa crear una `Revision` nueva con
`previous_revision_id` apuntando a la anterior.

## Estados de una Revision

```
DRAFT ──────► RELEASED ──────► DEPRECATED
```

- **DRAFT**: en trabajo, visible solo a quien la crea/edita, no es
  candidata a `current_revision` de un Component salvo que el Component
  mismo esté en DRAFT.
- **RELEASED**: revisión activa/oficial. Puede ser `current_revision` de
  su Component.
- **DEPRECATED**: fue reemplazada por una Revision posterior; se conserva
  para siempre, nunca se borra.

No hay estado de "branching" en el MVP (el segundo bloque lo menciona como
"si fuese necesario" — no hay caso de uso real hoy que lo justifique;
`previous_revision_id` es una cadena lineal, no un árbol).

## Reglas de integridad

1. `revisions.created_at` nunca se actualiza; no existe `updated_at` en
   esta tabla — es la garantía de inmutabilidad a nivel de schema.
2. Cambiar `current_revision_id` de un `Component` es la única escritura
   permitida sobre `components` que el flujo de "nueva revisión" dispara;
   no se reescribe contenido de revisiones pasadas.
3. Al crear una Revision `RELEASED` nueva para un Component, la Revision
   anterior que tenía `status='RELEASED'` pasa a `DEPRECATED` en la misma
   transacción.
4. `label` es libre (texto), pero por convención: letras para hardware
   (A, B, C...) y semver para software (0.1, 0.2, 1.0...) — no se fuerza
   por constraint, es convención documentada en el template de Component
   (`platform/templates/component.md`).

## Reconstrucción de historial

```sql
WITH RECURSIVE history AS (
  SELECT * FROM revisions WHERE id = :revision_id
  UNION ALL
  SELECT r.* FROM revisions r
  JOIN history h ON r.id = h.previous_revision_id
)
SELECT * FROM history ORDER BY created_at;
```

Esto es lo que alimenta la "Revision History UI" de la Component Page
(Fase 9) y lo que el AI assistant usa para responder "¿qué cambió entre
Rev A y Rev B?" (compara `change_summary`/`description` de las dos filas).

## Draft vs Released a nivel Component

`components.status` (DRAFT/DESIGN/PROTOTYPE/TESTING/VALIDATED/RELEASED/
DEPRECATED) es independiente del `status` de sus Revisions individuales —
el primero describe la madurez del Component como concepto de ingeniería,
el segundo el estado de publicación de una versión puntual. Un Component
`RELEASED` puede perfectamente tener una Revision `DRAFT` en trabajo para
la siguiente iteración.
