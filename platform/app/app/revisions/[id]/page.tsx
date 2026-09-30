import Link from "next/link";
import { notFound } from "next/navigation";
import { prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function RevisionPage({ params }: { params: { id: string } }) {
  const revision = await prisma.revision.findUnique({
    where: { id: params.id },
    include: {
      component: true,
      artifacts: true,
      author: { select: { name: true, email: true } },
      previousRevision: true,
      nextRevisions: true,
    },
  });

  if (!revision) return notFound();

  const documents = await prisma.document.findMany({
    where: { entityType: "REVISION", entityId: revision.id },
  });

  const tests = await prisma.test.findMany({
    where: {
      targetComponentId: revision.componentId,
      build: { buildComponents: { some: { revisionId: revision.id } } },
    },
  });

  return (
    <div>
      <p>
        <Link href="/">← Dashboard</Link> /{" "}
        <Link href={`/components/${revision.component.id}`}>{revision.component.name}</Link>
      </p>
      <h1>
        {revision.component.name} — Rev {revision.label}
      </h1>
      <span className="badge">{revision.status}</span>
      <p>{revision.description}</p>

      <div className="card">
        <h2>Changes</h2>
        <p>{revision.changeSummary ?? "Sin resumen de cambio."}</p>
        <p>
          Autor: {revision.author.name} ({revision.author.email}) — {revision.createdAt.toISOString().slice(0, 10)}
        </p>
        {revision.previousRevision && (
          <p>
            Revisión anterior:{" "}
            <Link href={`/revisions/${revision.previousRevision.id}`}>Rev {revision.previousRevision.label}</Link>
          </p>
        )}
        {revision.nextRevisions.length > 0 && (
          <p>
            Reemplazada por:{" "}
            {revision.nextRevisions.map((r) => (
              <Link key={r.id} href={`/revisions/${r.id}`}>
                Rev {r.label}{" "}
              </Link>
            ))}
          </p>
        )}
      </div>

      <div className="card">
        <h2>Files</h2>
        <ul>
          {revision.artifacts.map((a) => (
            <li key={a.id}>
              <a href={`/api/artifacts/${a.id}`}>{a.filename}</a> ({a.fileType})
            </li>
          ))}
          {revision.artifacts.length === 0 && <li>Ningún archivo subido.</li>}
        </ul>
      </div>

      <div className="card">
        <h2>Documents</h2>
        <ul>
          {documents.map((d) => (
            <li key={d.id}>{d.title}</li>
          ))}
          {documents.length === 0 && <li>Ningún documento vinculado a esta revisión específica.</li>}
        </ul>
      </div>

      <div className="card">
        <h2>Tests</h2>
        <ul>
          {tests.map((t) => (
            <li key={t.id}>
              {t.name} <span className="badge">{t.result}</span>
            </li>
          ))}
          {tests.length === 0 && <li>Ningún test registrado contra un build que use esta revisión.</li>}
        </ul>
      </div>
    </div>
  );
}
