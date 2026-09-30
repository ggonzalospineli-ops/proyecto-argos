import { prisma } from "./db";

// Busqueda global full-text (PostgreSQL to_tsvector, calculado on-the-fly
// via SQL crudo en vez de columna generada — simplificacion documentada
// en PHASE_9_REPORT.md). Semantic/vector search queda fuera del MVP, ver
// DATABASE_SCHEMA.md.

export interface SearchResult {
  type: "component" | "document";
  id: string;
  title: string;
  snippet: string;
}

export async function globalSearch(query: string): Promise<SearchResult[]> {
  if (!query.trim()) return [];

  const components = await prisma.$queryRaw<
    { id: string; name: string; description: string | null }[]
  >`
    SELECT id, name, description
    FROM components
    WHERE to_tsvector('spanish', coalesce(name, '') || ' ' || coalesce(description, ''))
      @@ plainto_tsquery('spanish', ${query})
    LIMIT 20
  `;

  const documents = await prisma.$queryRaw<
    { id: string; title: string; content_markdown: string }[]
  >`
    SELECT id, title, content_markdown
    FROM documents
    WHERE to_tsvector('spanish', coalesce(title, '') || ' ' || coalesce(content_markdown, ''))
      @@ plainto_tsquery('spanish', ${query})
    LIMIT 20
  `;

  return [
    ...components.map((c) => ({
      type: "component" as const,
      id: c.id,
      title: c.name,
      snippet: c.description?.slice(0, 160) ?? "",
    })),
    ...documents.map((d) => ({
      type: "document" as const,
      id: d.id,
      title: d.title,
      snippet: d.content_markdown.slice(0, 160),
    })),
  ];
}
