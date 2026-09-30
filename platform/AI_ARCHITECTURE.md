# AI_ARCHITECTURE.md — Fase 7

## Flujo (preferido explícitamente por el usuario — sin multi-agente)

```
Usuario
 ↓ (pregunta en lenguaje natural)
AI endpoint (Fase 9: /api/ai/ask)
 ↓
1. Clasificación ligera de la pregunta → qué entidades probablemente
   involucra (heurística simple por keywords/nombre de entidad
   mencionado, NO un router con LLM adicional en el MVP)
 ↓
2. Structured queries sobre PostgreSQL (Prisma) — components, revisions,
   dependencies, builds, tests relevantes
 ↓
3. Full-text search sobre `documents` (tsvector) para contenido narrativo
   relacionado
 ↓
4. Se arma un contexto de texto con (2)+(3), cada fragmento con su
   referencia de origen (tabla + id, o document + id)
 ↓
5. LLM (vía AI Gateway o llamada directa a un provider — configurable por
   env var) recibe: pregunta + contexto + instrucción de grounding
   estricto
 ↓
Respuesta, con citas a las entidades/documentos usados
```

No hay embeddings, vector DB, ni grafo de relaciones separado en el MVP —
la "estructura" ES el grafo (las tablas relacionales de
`DATABASE_SCHEMA.md` ya codifican las relaciones; se recorren con SQL/
Prisma, no con un motor de grafos dedicado). Esto es consistente con la
regla explícita del usuario: "Do NOT start with a complex multi-agent
architecture... Do NOT start with autonomous agents."

## Componentes técnicos (Fase 9)

- **Endpoint**: una función server-side (`app/api/ai/ask/route.ts` en
  Next.js), no un servicio separado.
- **Query layer**: funciones Prisma reutilizadas de las mismas rutas que
  alimentan las páginas normales (Dashboard, Component Page, etc.) — no
  se duplica lógica de acceso a datos para la IA.
- **LLM provider**: configurable vía `AI_PROVIDER` + `AI_API_KEY` (env
  vars, nunca hardcodeado). Si no hay credenciales configuradas, el
  endpoint devuelve un error claro ("AI assistant no configurado") en vez
  de fallar silenciosamente o inventar una respuesta.
- **Permisos**: el asistente respeta el rol del usuario autenticado que
  pregunta — un `VIEWER` obtiene las mismas respuestas que vería
  navegando la UI, nada más.

## Restricciones duras (no negociables, heredadas del prompt del usuario)

1. **Read-only**: el asistente nunca ejecuta `INSERT`/`UPDATE`/`DELETE`.
   Solo hace `SELECT`. No tiene tool-calling hacia mutaciones en el MVP.
2. **No autónomo**: responde preguntas puntuales, no ejecuta flujos de
   varios pasos sin supervisión, no genera Change Requests
   automáticamente.
3. **Grounding estricto**: ver `AI_CONTEXT_STRATEGY.md`. Si no hay datos,
   dice explícitamente que no hay información, no completa con
   conocimiento general del modelo.
4. **Fuera de alcance de contenido**: el asistente no genera contenido
   técnico de sistemas de guiado de misiles, seekers, ni de armamento —
   esto es un límite del proyecto completo (ver `PROJECT_CONTEXT.md`),
   no solo de este componente, y aplica independientemente de qué
   pregunte el usuario final de la plataforma.

## Por qué no un grafo dedicado (Neo4j u otro)

El primer bloque del usuario es explícito: "PostgreSQL relationships are
sufficient initially" y "Do NOT create... a separate graph database". Las
consultas de dependencias (`depends_on`/`contains`) son 1-2 saltos en la
práctica (rara vez más de 3-4 niveles en un dron), perfectamente
manejables con CTEs recursivas de Postgres (ya usadas en `BOM_MODEL.md`).
