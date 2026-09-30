# CAD_FORMAT_MATRIX.md — Fase 4

Formato final que va a usar el equipo: **TO BE DEFINED** (ver
`OPEN_QUESTIONS.md`). La matriz de abajo es de referencia general de la
industria, no una confirmación de qué usa Argos.

| Formato | Preview navegador (Three.js) | Metadata útil embebida | Editable en plataforma | Versionable como Artifact | Diffable geométrico |
|---|---|---|---|---|---|
| STL | Sí — mesh directo, soportado nativamente por three.js STLLoader | Mínima (solo geometría, sin metadata) | No | Sí | No (fuera de alcance, requeriría motor de diff geométrico) |
| 3MF | Sí — three.js 3MFLoader | Moderada (puede incluir color/material) | No | Sí | No |
| STEP | No directo — requiere conversión server-side a mesh (fuera del MVP) | Alta (geometría paramétrica, ensamblados, metadata de fabricante) | No | Sí (se guarda el archivo, no se previsualiza) | No |
| OBJ | Sí — three.js OBJLoader | Moderada (con .mtl) | No | Sí | No |
| DXF | No | Baja (2D) | No | Sí | No |
| PDF (planos, drawings) | No (se abre con el visor de PDF del navegador, no con el 3D viewer) | N/A | No | Sí | No |

## Decisión para el MVP

Priorizar preview de **STL y 3MF** (regla explícita del usuario, sección
7 del tercer bloque: "Priority: STL / 3MF preview"). STEP y otros formatos
se almacenan y se pueden descargar, pero no se previsualizan en el
navegador en el MVP — evita meter un conversor STEP→mesh server-side, que
es complejidad significativa fuera del alcance acordado.
