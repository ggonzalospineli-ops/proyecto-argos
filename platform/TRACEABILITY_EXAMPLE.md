# TRACEABILITY_EXAMPLE.md — Fase 6

Ejemplo completo end-to-end de la cadena de trazabilidad que soporta el
modelo. **Todos los datos de este documento son ficticios /
ilustrativos** — no representan componentes, builds ni tests reales de
Argos (ver `CURRENT_COMPONENTS.md` para el inventario real, que hoy está
vacío de hardware confirmado).

## Escenario [EJEMPLO — no real]

```
Component: "Motor Mount" [EJEMPLO]
  Revision A (DEPRECATED)
    Artifact: motor-mount-a.step
  Revision B (RELEASED, current)
    Artifact: motor-mount-b.step
    Artifact: motor-mount-b.stl
    Document: "Design Notes — Rev B" — "Se reforzó el punto de anclaje
      tras vibración observada en TEST-001"

Dependency: Motor Mount --depends_on--> Motor [EJEMPLO]
BOMLine: Arm --contains x4--> Motor Mount [EJEMPLO]

Build: "ARGOS-01 Build #001" [EJEMPLO]
  build_components: Motor Mount → Revision A
                     Arm → Revision B
                     Motor → Revision A

Test: "TEST-001 — Motor Mount vibration check" [EJEMPLO]
  target: Motor Mount
  build: ARGOS-01 Build #001
  result: FAIL
  notes: "Grieta visible tras 10 min de vuelo estacionario"

[resultado] → Document change-request.md: "CR-001: reforzar punto de
  anclaje del Motor Mount" → nueva Revision B (RELEASED) → 
  Test: "TEST-004 — Motor Mount vibration check (retest)" [EJEMPLO]
    target: Motor Mount, build: (nuevo build, o retest directo)
    result: PASS
```

## Cadena de trazabilidad recorrida

```
Requirement (POST-MVP, no aplica en este ejemplo)
  → Component: Motor Mount
    → Revision A → Build #001 → Test-001 → FAIL
    → (Issue documentado vía Document, template issue.md)
    → Change Request (Document, template change-request.md)
    → Revision B (nueva)
      → Test-004 → PASS
```

## Preguntas que esta cadena responde (con datos de ejemplo)

- *"¿Qué revisión de Motor Mount se usó en Build #001?"* → Revision A.
- *"¿Por qué se creó la Revision B?"* → `revisions.change_summary` de B +
  el Document de Design Notes citan TEST-001 y el FAIL observado.
- *"¿Qué tests tiene la Revision actual del Motor Mount?"* → TEST-004
  (PASS), vía `target_component_id` + filtrando por builds que usan la
  Revision current.

Esta es exactamente la estructura que el AI Assistant (Fase 7) recorre
para responder preguntas de trazabilidad — ver `AI_CONTEXT_STRATEGY.md`.
