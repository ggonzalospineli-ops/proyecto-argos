# KNOWLEDGE_MODEL.md — Fase 3

Qué información vive dónde, para que tanto humanos como el AI assistant
(Fase 7) sepan dónde buscar.

| Tipo de información | Dónde vive | Por qué |
|---|---|---|
| Identidad y metadata estructurada (nombre, tipo, estado, jerarquía, cantidades, fechas) | PostgreSQL (tablas de `DATABASE_SCHEMA.md`) | Necesita queries exactas, joins, agregaciones — es lo que responde "¿qué depende de qué?", "¿qué revisión está activa?". |
| Explicaciones, decisiones, contexto narrativo ("por qué elegimos X") | `documents.content_markdown` | Texto libre, no estructurado, pensado para lectura humana y para RAG. |
| Archivos binarios (CAD, fotos, exports) | Object storage, referenciados por `artifacts` | No pertenecen en la base de datos relacional; solo su metadata sí. |
| Indexado semánticamente | **Ninguno todavía** — full-text (`tsvector`) en `components.search_vector` y `documents.search_vector` cubre el MVP. Vector search es POST-MVP (ver `DATABASE_SCHEMA.md`, sección de búsqueda). | Regla explícita del usuario: semantic search es opcional en la primera iteración. |

## Regla para decidir dónde va un dato nuevo

1. ¿Se necesita filtrar/ordenar/agregar por este dato con precisión
   (ej. "todos los componentes en estado TESTING")? → columna estructurada
   en Postgres.
2. ¿Es explicación en prosa que un humano necesita leer para entender el
   contexto? → `Document`.
3. ¿Es un archivo binario? → `Artifact` + object storage.
4. Si dudás entre 1 y 2, preferí estructurado — es más barato agregar un
   campo de texto libre después que migrar texto libre a estructurado.

## Contexto para el AI Assistant (adelanto de Fase 7)

El asistente arma su contexto combinando (1) resultados de queries
estructuradas sobre Postgres y (2) el contenido de `Documents` enlazados
a las entidades relevantes — nunca solo uno de los dos. El detalle de
cómo se combinan está en `AI_CONTEXT_STRATEGY.md`.
