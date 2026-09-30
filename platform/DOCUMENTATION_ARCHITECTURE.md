# DOCUMENTATION_ARCHITECTURE.md — Fase 3

## Estructura de carpetas propuesta (para cuando haya contenido real)

```
/docs
  /system            # documentos a nivel Project/System (visión, arquitectura)
  /subsystems
  /components        # un doc por Component relevante (design/manufacturing/test notes)
  /requirements       # post-MVP — placeholder de convención, no hay requirements todavía
  /tests
  /decisions         # ADRs, incluye decisiones de hardware y software
  /manufacturing
  /software
```

Esta carpeta física (`/docs` en la raíz del repo o dentro de
`platform/app/docs/` según se decida en Fase 9) es un **espejo de
lectura/exportación**, no la fuente de verdad: la fuente de verdad de cada
`Document` es la fila en la tabla `documents` (`content_markdown`). La
estructura de carpetas sirve para navegación humana fuera de la app (ej.
en el propio repo git) y para exportar/hacer backup, no para almacenar el
contenido editable — evita divergencia entre "el archivo en disco" y "lo
que la app muestra".

En el MVP (Fase 9), los documentos viven únicamente en la base de datos,
editables desde la Component/System/Build/Test page. La exportación a
`/docs` como archivos reales queda como mejora post-MVP si se necesita
integrar con git.

## Por qué documentos y no un wiki completo

Regla del usuario: "Do NOT build a full Notion/Confluence clone. Markdown
+ basic editor is enough." El MVP implementa: crear, editar (markdown
plano en un textarea/editor simple), ver (renderizado), enlazar a una
entidad. No hay: versionado de documentos independiente del versionado de
Revisions, comentarios, permisos granulares por documento, ni carpetas
anidadas dentro de la app (la jerarquía de carpetas de arriba es solo
para exportación).

## Relación con el versionamiento de Components

Un `Document` vinculado a un `Component` (`entity_type='COMPONENT'`) es
"vivo" — se edita en el lugar, no versiona junto a las Revisions. Si un
documento necesita fijarse a una Revision específica (ej. "estas son las
notas de diseño que corresponden exactamente a la Rev B"), se vincula con
`entity_type='REVISION'` y `entity_id=<revision_id>` en vez de al
Component. Esa es la única distinción que necesita el modelo — no hace
falta versionar el documento en sí.
