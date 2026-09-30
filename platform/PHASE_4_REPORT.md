# PHASE_4_REPORT.md

**Objective**: Definir cómo entran los archivos reales (CAD y otros
artifacts) al sistema.

**Completed**
- `ARTIFACT_MODEL.md` — campos, interfaz `ArtifactStorage` abstracta
  (local filesystem para dev, S3-compatible para prod vía swap de
  driver), reglas de qué NO hace el modelo (no parsea CAD, no versiona
  in-place).
- `CAD_WORKFLOW.md` — flujo CAD→Export→Revision→Upload→Review→
  Manufacturing→Test, con los límites explícitos de qué queda fuera
  (sin integración con herramientas CAD, sin generación de manufacturing
  files, sin CAD editing).
- `CAD_FORMAT_MATRIX.md` — matriz de formatos (STL, 3MF, STEP, OBJ, DXF,
  PDF) evaluando preview/metadata/editable/versionable/diffable, con
  STL/3MF priorizados para preview según regla explícita del usuario.

**Not completed**
- 3D Viewer PoC: **diferido a Fase 9**, tal como permite el propio prompt
  del usuario ("If 3D preview significantly increases MVP complexity,
  make it a separate optional milestone"). Se implementa como componente
  React dentro de `platform/app/` una vez que exista la app base, no como
  entregable de Fase 4 aislado.

**Decisions**
- Todo Artifact cuelga obligatoriamente de una Revision (nunca de un
  Component directo) — fuerza disciplina de versionado desde el modelo de
  datos, no solo por convención.
- Preview 3D limitado a STL/3MF en el MVP; STEP y otros formatos se
  almacenan/descargan sin preview.

**Unknowns**
- Formato(s) CAD que realmente va a usar el equipo (heredado de Fase 0 —
  sigue TO BE DEFINED).

**Risks**
- Si el equipo termina trabajando casi exclusivamente en STEP (típico en
  CAD paramétrico serio como Fusion 360/SolidWorks), la falta de preview
  en el MVP reduce bastante el valor del "3D Viewer" hasta que se agregue
  conversión server-side — vale la pena confirmar el formato real pronto
  para no descubrir esto tarde.

**Next phase**: Fase 5 — Versionamiento e ingeniería de cambios.

**Recommended actions**
- Confirmar con el equipo de hardware qué formato de exportación van a
  usar de forma rutinaria, para priorizar correctamente el trabajo de
  preview 3D en Fase 9.
