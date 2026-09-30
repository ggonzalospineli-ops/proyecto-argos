# AUDIT_MODEL.md — Fase 5

## Qué se audita en el MVP (implícito en el modelo, sin tabla dedicada)

El modelo de datos del MVP ya captura la mayoría del rastro de auditoría
sin necesitar una tabla `audit_log` separada, porque las entidades clave
son inmutables o casi-inmutables:

| Pregunta de auditoría | Cómo se responde en el MVP |
|---|---|
| ¿Quién creó esta Revision y cuándo? | `revisions.author_id`, `revisions.created_at` |
| ¿Qué cambió respecto a la anterior? | `revisions.change_summary`, comparado con `previous_revision_id` |
| ¿Quién subió este archivo? | `artifacts.uploaded_by`, `artifacts.uploaded_at` |
| ¿Quién escribió este documento? | `documents.author_id` |
| ¿Quién registró este test y cuándo? | `tests.created_by`, `tests.date` |

## Qué NO se audita en el MVP (gap consciente)

- Ediciones de campos mutables (ej. cambiar `components.status`,
  `components.description`, o editar un `Document` existente) **no**
  quedan registradas con "estado anterior / estado nuevo" — Postgres solo
  guarda `updated_at`, no un historial de cambios de esos campos.
- No hay tabla `audit_log` genérica con `(actor, timestamp, acción,
  entidad, previous_state, new_state, reason)` como pide el tercer bloque
  del usuario en su sección 24 — eso es POST-MVP.

## Diseño POST-MVP (documentado, no implementado)

```sql
CREATE TABLE audit_log (
  id UUID PRIMARY KEY,
  actor_id UUID NOT NULL REFERENCES users(id),
  action TEXT NOT NULL,           -- ej. 'component.status_changed'
  entity_type TEXT NOT NULL,
  entity_id UUID NOT NULL,
  previous_state JSONB,
  new_state JSONB,
  reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Se poblaría con un trigger genérico o middleware de la capa de
aplicación (ej. un wrapper de Prisma) que intercepte updates sobre las
tablas mutables. Se difiere del MVP porque el volumen de datos/usuarios
actual no lo justifica todavía (regla de "no construir antes de tener un
caso de uso real").

## Recomendación práctica mientras tanto

Para Components y Systems (las entidades mutables sin historial), la
convención de equipo debería ser: cualquier cambio de `status` o de
`description` que valga la pena recordar se documenta como una entrada
nueva en el Document de "Design Notes" del Component (con fecha), no se
pierde silenciosamente — es un paliativo manual, no un sustituto real de
auditoría automática.
