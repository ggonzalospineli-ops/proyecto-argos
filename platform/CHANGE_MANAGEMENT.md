# CHANGE_MANAGEMENT.md — Fase 5

Diseño del flujo de cambio. **No se implementa como entidad/UI dedicada
en el MVP** (`ChangeRequest` es POST-MVP, ver `ENTITY_CATALOG.md`) — se
documenta acá para que el proceso manual de hoy ya siga esta forma, y
para que la futura entidad `ChangeRequest` tenga un diseño claro cuando
se decida construirla.

## Flujo conceptual

```
Change Request (propuesta, hoy: Document con template change-request.md)
  → Impact Analysis (hoy: manual, completando la sección del template;
                      automatizado en el futuro, ver IMPACT_ANALYSIS.md)
  → Review (hoy: fuera de la plataforma — conversación entre el equipo)
  → Approval (hoy: se refleja simplemente en que alguien crea la Revision)
  → Revision (nueva Revision del Component, status=DRAFT)
  → Test (Tests ejecutados contra un Build que use esa Revision)
  → Release (Revision pasa a status=RELEASED)
```

## Cómo se usa esto HOY, en el MVP

1. Alguien identifica que un Component necesita cambiar.
2. Crea un `Document` usando `templates/change-request.md`, enlazado al
   Component.
3. Completa manualmente "componentes/dependencias afectados" mirando la
   sección Dependencies/Dependents de la Component Page.
4. Crea una nueva `Revision` (DRAFT) con el cambio real.
5. Sube artifacts/documenta el cambio.
6. Corre los tests que correspondan, los registra.
7. Cuando está conforme, marca la Revision como `RELEASED`.

No hay estado de "pendiente de aprobación" que bloquee nada en el MVP —
el control es social/de proceso del equipo, no impuesto por la
plataforma. Esto es consistente con la regla del usuario: la IA (y en
este caso, la plataforma en general) no auto-aprueba ni auto-aplica
cambios.

## Cuándo formalizar `ChangeRequest` como entidad

Cuando el volumen de cambios simultáneos o el tamaño del equipo hagan que
rastrear esto vía Documents individuales sea insuficiente (señal
concreta: más de un par de CRs abiertos a la vez, o necesidad de que
alguien externo apruebe formalmente antes de que se pueda crear la
Revision). En ese punto, se agrega la tabla `change_requests` con un
`status` real que bloquee la creación de la Revision hasta `APPROVED`.
