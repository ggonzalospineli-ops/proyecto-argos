# IMPACT_ANALYSIS.md — Fase 8

**Estado: diseño POST-MVP.** No se implementa funcionalmente en Fase 9 —
el "Practical MVP Boundary" del usuario no incluye impact analysis
automatizado entre sus 12 puntos de alcance. Se documenta acá para que
sea directo de construir cuando se decida abordarlo, apoyándose 100% en
el modelo de datos ya definido en Fases 1-2 (no requiere cambios de
schema).

## Qué significa "impacto" en este modelo

Dado un Component que se quiere modificar, el impacto se calcula
recorriendo el grafo de `component_dependencies` y `bom_lines` ya
existente:

```
Direct dependencies   = component_dependencies WHERE to_component_id = :id AND type='DEPENDS_ON'
Indirect dependencies = clausura transitiva de lo anterior (CTE recursiva)
Affected builds        = build_components WHERE component_id = :id
                          (builds que usaron ESTE componente en cualquier revisión)
Affected tests          = tests WHERE target_component_id = :id
                          OR target_component_id IN (indirect dependents)
Affected documents      = documents WHERE entity_id IN (component ∪ sus revisions)
```

## Query de dependientes indirectos (clausura transitiva)

```sql
WITH RECURSIVE dependents AS (
  SELECT from_component_id AS component_id, 1 AS depth
  FROM component_dependencies
  WHERE to_component_id = :target_id AND type = 'DEPENDS_ON'

  UNION

  SELECT cd.from_component_id, d.depth + 1
  FROM component_dependencies cd
  JOIN dependents d ON cd.to_component_id = d.component_id
  WHERE cd.type = 'DEPENDS_ON'
)
SELECT DISTINCT component_id, MIN(depth) AS distance FROM dependents GROUP BY component_id;
```

## Flujo de uso (post-MVP)

```
Usuario: "Quiero modificar Motor Mount."
Sistema:
  Affected components (directos + indirectos, con distancia)
  Affected builds (todos los que usaron cualquier revisión de Motor Mount)
  Affected tests (los que targetearon Motor Mount o sus dependientes)
  Affected documents (docs enlazados a Motor Mount o sus revisiones)
→ El asistente de IA (Fase 7) puede presentar esto en lenguaje natural,
  citando cada entidad — pero el cálculo en sí es SQL determinístico, no
  el LLM "adivinando" impacto.
```

## Change Proposal (post-MVP)

Una vez calculado el impacto, la IA podría generar una propuesta
estructurada (cambio solicitado + componentes afectados + riesgos +
documentación afectada + tests sugeridos) — el prompt del usuario es
explícito: **"La IA NO aplica automáticamente el cambio."** Esto sigue
siendo un output de solo lectura/sugerencia incluso cuando se implemente,
consistente con las restricciones de `AI_ARCHITECTURE.md`.

## Por qué queda fuera del MVP

1. No aporta valor hasta que haya suficientes Components y Dependencies
   reales cargados como para que "impacto" sea algo no trivial de ver a
   simple vista.
2. El "Practical MVP Boundary" es explícito en no incluirlo (sección 27
   del tercer bloque lo lista como parte de "Después", no del MVP
   inicial).
3. La UI de Dependencies/Dependents de la Component Page (sí incluida en
   el MVP) ya cubre la necesidad más básica de "¿qué se ve afectado?" a
   un salto de distancia — la clausura transitiva completa es la mejora
   incremental natural, no un requisito de arranque.
