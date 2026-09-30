# ARGOS_SYSTEM_MODEL_DIAGRAM.md — Fase 1

Diagrama visual del modelo conceptual (Mermaid). Todos los nombres de
componentes son `[EJEMPLO]` — ilustran el modelo, no representan
inventario real confirmado (ver `CURRENT_COMPONENTS.md`).

```mermaid
graph TD
    PROJ["Project: ARGOS 1"]
    SYS_A["System: Airframe [EJEMPLO]"]
    SYS_P["System: Propulsion [EJEMPLO]"]
    SYS_S["System: Software [EJEMPLO]"]
    SUB_FS["Subsystem: Flight Software [EJEMPLO]"]

    COMP_MM["Component: Motor Mount [EJEMPLO]"]
    COMP_ARM["Component: Arm [EJEMPLO]"]
    COMP_MOTOR["Component: Motor [EJEMPLO]"]

    REV_A["Revision A"]
    REV_B["Revision B"]
    ART_STEP["Artifact: motor-mount.step"]
    ART_STL["Artifact: motor-mount.stl"]
    DOC_DESIGN["Document: design-notes.md"]

    BUILD["Build: ARGOS-01 #001"]
    TEST["Test: TEST-001 (PASS)"]

    PROJ --> SYS_A
    PROJ --> SYS_P
    PROJ --> SYS_S
    SYS_S --> SUB_FS

    SYS_A --> COMP_MM
    SYS_A --> COMP_ARM
    SYS_P --> COMP_MOTOR

    COMP_MM -- depends_on --> COMP_MOTOR
    COMP_ARM -- contains x4 --> COMP_MM

    COMP_MM --> REV_A
    COMP_MM --> REV_B
    REV_B --> ART_STEP
    REV_B --> ART_STL
    REV_B --> DOC_DESIGN

    BUILD -- uses Rev A --> COMP_MM
    BUILD --> TEST
    TEST -- target --> COMP_MM
```

## Lectura del diagrama

- `Project → System → Subsystem → Component` es la jerarquía de
  navegación (System Explorer, Fase 9).
- `Component → Revision → Artifact/Document` es la cadena versionada.
- `depends_on` y `contains` son aristas horizontales entre Components,
  independientes de la jerarquía de navegación.
- `Build` congela qué `Revision` de cada `Component` se usó; `Test`
  cuelga de `Build` y/o `Component`.
