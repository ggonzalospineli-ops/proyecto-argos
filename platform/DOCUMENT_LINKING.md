# DOCUMENT_LINKING.md — Fase 3

## Modelo de enlace

`documents.entity_type` + `documents.entity_id` (FK polimórfica, ver
`DATABASE_SCHEMA.md`). Un `Document` enlaza a exactamente una entidad:

```
Document → entity_type ∈ {SYSTEM, COMPONENT, REVISION, BUILD, TEST}
Document → entity_id = id de esa entidad
```

No hay enlace N:N documento-múltiples-entidades en el MVP (mantiene el
modelo simple). Si un mismo contenido aplica a varias entidades, se
duplica el documento o se enlaza a la entidad más general (ej. al
`Component` en vez de repetirlo en cada `Revision`).

## Cadena de navegación típica

```
Component
 ├─ documents WHERE entity_type='COMPONENT' AND entity_id=component.id
 └─ Revision (current)
     ├─ artifacts WHERE revision_id = revision.id
     └─ documents WHERE entity_type='REVISION' AND entity_id=revision.id
```

Ejemplo ilustrativo (no real):
```
Motor Mount [EJEMPLO]
├── Document: "Design Notes" (entity_type=COMPONENT)
├── Document: "Manufacturing Notes" (entity_type=COMPONENT)
└── Revision B
    ├── Artifact: motor-mount.step
    ├── Artifact: motor-mount.stl
    └── Document: "Test Notes — Rev B" (entity_type=REVISION)
```

## Por qué polimórfico y no 5 tablas de unión

5 tablas de unión (`system_documents`, `component_documents`, ...)
serían más "correctas" relacionalmente, pero para un MVP con volumen bajo
de documentos, una columna `entity_type` + índice compuesto
`(entity_type, entity_id)` es suficientemente rápido y evita 5 modelos
Prisma casi idénticos. Si el volumen de documentos crece mucho y la falta
de integridad referencial de DB se vuelve un problema real, es una
migración directa a tablas de unión — no un cambio de modelo conceptual.
