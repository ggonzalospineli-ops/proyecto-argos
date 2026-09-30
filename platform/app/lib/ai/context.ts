import { prisma } from "../db";

// Arma el contexto para el AI assistant siguiendo AI_CONTEXT_STRATEGY.md:
// STRUCTURED CONTEXT + DOCUMENT CONTEXT, cada fragmento con su fuente
// citable. Sin LLM router: heuristica simple (ILIKE sobre nombres de
// Component/System) + fallback a full-text search si no matchea nada.

export interface ContextFragment {
  source: string; // ej. "Component: Motor Mount (id=...)"
  text: string;
}

async function findMentionedComponents(question: string) {
  const words = question
    .split(/\s+/)
    .map((w) => w.replace(/[^\p{L}\p{N}]/gu, ""))
    .filter((w) => w.length > 2);

  if (words.length === 0) return [];

  return prisma.component.findMany({
    where: {
      OR: words.map((w) => ({ name: { contains: w, mode: "insensitive" as const } })),
    },
    take: 10,
  });
}

async function findMentionedSystems(question: string) {
  const words = question
    .split(/\s+/)
    .map((w) => w.replace(/[^\p{L}\p{N}]/gu, ""))
    .filter((w) => w.length > 2);

  if (words.length === 0) return [];

  return prisma.system.findMany({
    where: {
      OR: words.map((w) => ({ name: { contains: w, mode: "insensitive" as const } })),
    },
    take: 10,
  });
}

export async function buildContext(question: string): Promise<ContextFragment[]> {
  const fragments: ContextFragment[] = [];

  const [components, systems] = await Promise.all([
    findMentionedComponents(question),
    findMentionedSystems(question),
  ]);

  for (const system of systems) {
    const children = await prisma.component.findMany({
      where: { parentSystemId: system.id },
      select: { name: true, status: true, type: true },
    });
    fragments.push({
      source: `System: ${system.name} (id=${system.id})`,
      text: `Estado: ${system.status}. Descripcion: ${system.description ?? "(sin descripcion)"}. Componentes directos: ${
        children.length ? children.map((c) => `${c.name} [${c.type}, ${c.status}]`).join(", ") : "ninguno registrado"
      }.`,
    });
  }

  for (const component of components) {
    const [currentRevision, dependencies, dependents, docs] = await Promise.all([
      component.currentRevisionId
        ? prisma.revision.findUnique({ where: { id: component.currentRevisionId } })
        : null,
      prisma.componentDependency.findMany({
        where: { fromComponentId: component.id },
        include: { toComponent: { select: { name: true } } },
      }),
      prisma.componentDependency.findMany({
        where: { toComponentId: component.id },
        include: { fromComponent: { select: { name: true } } },
      }),
      prisma.document.findMany({
        where: { entityType: "COMPONENT", entityId: component.id },
        select: { title: true, contentMarkdown: true, id: true },
      }),
    ]);

    fragments.push({
      source: `Component: ${component.name} (id=${component.id})`,
      text: `Tipo: ${component.type}. Estado: ${component.status}. Descripcion: ${
        component.description ?? "(sin descripcion)"
      }. Revision actual: ${currentRevision ? currentRevision.label : "(ninguna definida)"}. Dependencias (depends_on/contains/compatible_with hacia otros): ${
        dependencies.length
          ? dependencies.map((d) => `${d.type} -> ${d.toComponent.name}`).join(", ")
          : "ninguna registrada"
      }. Dependientes (otros componentes que dependen de este): ${
        dependents.length
          ? dependents.map((d) => `${d.fromComponent.name} (${d.type})`).join(", ")
          : "ninguno registrado"
      }.`,
    });

    for (const doc of docs) {
      fragments.push({
        source: `Document: "${doc.title}" (id=${doc.id}, componente=${component.name})`,
        text: doc.contentMarkdown.slice(0, 2000),
      });
    }

    // Revisiones + historial breve
    const revisions = await prisma.revision.findMany({
      where: { componentId: component.id },
      orderBy: { createdAt: "asc" },
      select: { label: true, status: true, changeSummary: true, description: true, createdAt: true },
    });
    if (revisions.length) {
      fragments.push({
        source: `Revisions: ${component.name} (id=${component.id})`,
        text: revisions
          .map(
            (r) =>
              `Rev ${r.label} [${r.status}] (${r.createdAt.toISOString().slice(0, 10)}): ${
                r.changeSummary ?? r.description ?? "(sin resumen de cambio)"
              }`
          )
          .join(" | "),
      });
    }

    // Builds y tests relacionados
    const buildComponents = await prisma.buildComponent.findMany({
      where: { componentId: component.id },
      include: { build: { select: { code: true, status: true } }, revision: { select: { label: true } } },
    });
    if (buildComponents.length) {
      fragments.push({
        source: `Builds using: ${component.name} (id=${component.id})`,
        text: buildComponents
          .map((bc) => `${bc.build.code} [${bc.build.status}] usa Rev ${bc.revision.label}`)
          .join(" | "),
      });
    }

    const tests = await prisma.test.findMany({
      where: { targetComponentId: component.id },
      select: { name: true, result: true, date: true, notes: true },
    });
    if (tests.length) {
      fragments.push({
        source: `Tests: ${component.name} (id=${component.id})`,
        text: tests
          .map((t) => `${t.name} [${t.result}] (${t.date.toISOString().slice(0, 10)}): ${t.notes ?? ""}`)
          .join(" | "),
      });
    }
  }

  // Fallback: si no se identifico ninguna entidad, full-text search general.
  if (fragments.length === 0) {
    const docs = await prisma.$queryRaw<{ id: string; title: string; content_markdown: string }[]>`
      SELECT id, title, content_markdown
      FROM documents
      WHERE to_tsvector('spanish', coalesce(title, '') || ' ' || coalesce(content_markdown, ''))
        @@ plainto_tsquery('spanish', ${question})
      LIMIT 5
    `;
    for (const doc of docs) {
      fragments.push({
        source: `Document: "${doc.title}" (id=${doc.id})`,
        text: doc.content_markdown.slice(0, 2000),
      });
    }
  }

  return fragments;
}
