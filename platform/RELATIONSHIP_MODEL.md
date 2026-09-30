# RELATIONSHIP_MODEL.md — Fase 1

Relaciones del modelo MVP. Las relaciones marcadas POST-MVP corresponden a
entidades no implementadas en Fase 9 (ver `ENTITY_CATALOG.md`).

## Relaciones estructurales (jerarquía)

```
Project      (1) ─── (N) System
System       (1) ─── (N) System            [subsistemas, self-referencial]
System       (1) ─── (N) Component         [parent_type = 'system']
Component    (1) ─── (N) Component         [parent_type = 'component', vía BOM]
Component    (1) ─── (N) Revision
Revision     (1) ─── (N) Artifact
```

## Relaciones de componente (MVP)

| Relación | Desde | Hacia | Cardinalidad | Significado |
|---|---|---|---|---|
| `depends_on` | Component | Component | N:N | "Este componente necesita que el otro exista/funcione para operar." |
| `contains` | Component | Component | N:N (vía BOMLine, con `quantity`) | Relación de BOM: ensamblado por. |
| `compatible_with` | Component | Component | N:N | Interoperabilidad conocida sin dependencia estructural. |

Todas se almacenan en una tabla `component_dependency` con columna `type`,
dirigida (`from_component_id → to_component_id`). La UI muestra:
- **Dependencies**: `type='depends_on' AND from_component_id = :id`
- **Dependents**: `type='depends_on' AND to_component_id = :id`
- El BOM se deriva de `type='contains'`.

## Relaciones documentales

```
Document  (N) ─── (1) [System | Component | Revision | Build | Test]   [polimórfica, entity_type + entity_id]
Artifact  (N) ─── (1) Revision
```

## Relaciones de build/test

```
Build           (1) ─── (N) BuildComponent   [congela component_id + revision_id]
BuildComponent  (N) ─── (1) Component
BuildComponent  (N) ─── (1) Revision
Test            (N) ─── (1) Build
Test            (N) ─── (1) Component
```

## Cadena de trazabilidad completa (MVP)

```
Component → Revision → Artifact
Component → Revision → Document
Build → BuildComponent(Component, Revision) → Test → result
```

Esto responde directamente las preguntas de ejemplo del usuario:
- *"¿Qué revisión de Motor Mount se usó en Build #001?"* → `Build → BuildComponent WHERE component = Motor Mount`.
- *"¿Qué componentes dependen de Motor Mount?"* → `component_dependency WHERE type='depends_on' AND to_component_id = Motor Mount`.
- *"¿Qué cambió entre Rev A y Rev B?"* → diff de `change_summary` + `description` entre dos filas de `Revision` del mismo `component_id`, ordenadas por `previous_revision_id`.

## Relaciones POST-MVP (documentadas, no implementadas)

```
Requirement   (N) ─── (N) Component        [implements]
Component     (N) ─── (N) Interface        [exposes]
Issue         (N) ─── (1) Build / Test
Issue         (1) ─── (N) ChangeRequest
ChangeRequest (1) ─── (1) Revision          [genera]
Decision      (N) ─── (N) [Component|System]  [related_to]
```
