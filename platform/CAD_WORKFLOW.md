# CAD_WORKFLOW.md — Fase 4

## Flujo

```
CAD (herramienta externa, ej. Fusion 360 / SolidWorks — TO BE DEFINED cuál usa el equipo)
  → Export (STEP/STL/3MF/otro)
  → Revision (se crea o se usa una Revision DRAFT existente del Component)
  → Upload (Artifact subido vía la Component/Revision Page)
  → Review (humano revisa antes de pasar la Revision a RELEASED)
  → Manufacturing (fuera del alcance del MVP — el archivo queda disponible para descarga/uso externo)
  → Test (resultados se registran como Test, ligados a la Revision vía el Build que la usa)
```

## Puntos de integración con el modelo

1. El diseñador exporta desde su herramienta CAD (fuera de la
   plataforma — no hay integración/plugin en el MVP).
2. Sube el archivo a través de la UI de la Component Page o Revision
   Page → crea/actualiza `Artifact` con `revision_id`.
3. Si es la primera vez que se sube algo para esta iteración de diseño,
   primero se crea la `Revision` (DRAFT) — el archivo nunca cuelga
   "suelto" de un Component sin Revision.
4. Marcar la Revision como `RELEASED` es una acción explícita separada de
   subir el archivo (permite subir varios artifacts de prueba antes de
   confirmar la revisión).

## Fuera de alcance (regla explícita del usuario)

- No hay integración directa con software CAD (plugins, APIs de Fusion
  360/SolidWorks).
- No hay generación automática de manufacturing files (G-code, sliced
  files) — eso es la fase "Manufacturing" del diagrama, fuera del MVP.
- No hay CAD editing ni modificación automática de geometría.
