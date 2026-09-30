# AI_CONTEXT_STRATEGY.md — Fase 7

## Tres capas de contexto, siempre separadas

```
STRUCTURED CONTEXT      → resultado de queries Prisma/SQL (hechos exactos:
                           nombres, estados, revisiones, fechas, cantidades,
                           relaciones depends_on/contains)
DOCUMENT CONTEXT         → contenido de `documents.content_markdown`
                           relevantes (full-text search por la pregunta +
                           documentos enlazados a las entidades ya
                           encontradas en STRUCTURED CONTEXT)
ARTIFACT METADATA        → filename/file_type/checksum/uploaded_at de
                           `artifacts` relevantes (nunca el contenido
                           binario del archivo — el LLM no puede "ver" un
                           STEP/STL)
```

Estas tres capas se concatenan en el prompt al LLM con delimitadores
claros y la fuente de cada fragmento (`[Component: Motor Mount, id=...]`,
`[Document: "Design Notes", id=...]`), para que el modelo pueda citar de
dónde sacó cada afirmación.

## System prompt (esqueleto, se ajusta en implementación)

```
Sos el asistente de ingeniería de Argos. Respondés preguntas ÚNICAMENTE
usando la información en STRUCTURED CONTEXT y DOCUMENT CONTEXT de abajo.

Reglas estrictas:
- Si la respuesta no está en el contexto, decí exactamente:
  "Information not defined in the current Argos knowledge base."
- No completes huecos con suposiciones ni conocimiento general sobre
  drones, ingeniería, o Argos como empresa.
- Toda afirmación importante debe citar su fuente (componente, revisión,
  documento, build o test específico).
- No propongas ni ejecutes cambios — sos de solo lectura.
```

## Ejemplo de armado de contexto (pregunta de ejemplo)

Pregunta: *"¿Qué componentes forman el Airframe?"*

1. STRUCTURED CONTEXT: `SELECT * FROM components WHERE parent_system_id =
   (SELECT id FROM systems WHERE name ILIKE 'Airframe')`.
2. DOCUMENT CONTEXT: `documents` enlazados a esos component_id +
   al system_id del Airframe.
3. Si la query (1) devuelve 0 filas → el contexto se arma vacío y el
   system prompt fuerza la respuesta de "no definido", nunca se le pide
   al LLM que "imagine" una respuesta plausible.

## Grounding: qué pasa cuando no hay datos

Regla explícita del usuario (sección 14 del tercer bloque / sección de
"AI Grounding" del primer bloque): si no hay información, la respuesta
es literalmente **"Information not defined in the current Argos
knowledge base."** — no una respuesta genérica sobre drones en general.
Esto se fuerza con:
1. Instrucción explícita en el system prompt (arriba).
2. Contexto vacío cuando las queries no devuelven resultados (nunca se
   rellena con "conocimiento de dominio" del LLM).
3. Test de integración en Fase 9 que verifique este comportamiento con
   una pregunta sobre una entidad que no existe.

## Source attribution

Cada respuesta debe adjuntar una lista de fuentes citadas (entity type +
id + nombre visible), que la UI del AI Assistant (Fase 9) renderiza como
links cliqueables hacia la Component/Revision/Document/Build/Test
correspondiente — así el usuario puede verificar la respuesta sin
confiar ciegamente en el LLM.
