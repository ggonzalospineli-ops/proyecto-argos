import Link from "next/link";
import { notFound } from "next/navigation";
import { prisma } from "@/lib/db";
import { Viewer3D } from "@/components/Viewer3D";

export const dynamic = "force-dynamic";

export default async function ComponentPage({ params }: { params: { id: string } }) {
  const component = await prisma.component.findUnique({
    where: { id: params.id },
    include: {
      currentRevision: { include: { artifacts: true } },
      revisions: { orderBy: { createdAt: "asc" } },
      dependenciesFrom: { include: { toComponent: true } },
      dependenciesTo: { include: { fromComponent: true } },
      buildComponents: { include: { build: true, revision: true } },
      testsAsTarget: true,
      parentSystem: true,
      parentComponent: true,
    },
  });

  if (!component) return notFound();

  const documents = await prisma.document.findMany({
    where: { entityType: "COMPONENT", entityId: component.id },
  });

  const previewArtifact = component.currentRevision?.artifacts.find((a) =>
    ["stl"].includes(a.fileType.toLowerCase())
  );

  return (
    <div>
      <p>
        <Link href="/">← Dashboard</Link>
        {component.parentSystem && (
          <>
            {" / "}
            <Link href={`/systems/${component.parentSystem.id}`}>{component.parentSystem.name}</Link>
          </>
        )}
        {component.parentComponent && (
          <>
            {" / "}
            <Link href={`/components/${component.parentComponent.id}`}>{component.parentComponent.name}</Link>
          </>
        )}
      </p>

      <h1>{component.name}</h1>
      <span className="badge">{component.type}</span> <span className="badge">{component.status}</span>
      <p>{component.description}</p>

      {previewArtifact && (
        <div className="card">
          <h2>3D Preview</h2>
          <Viewer3D artifactUrl={`/api/artifacts/${previewArtifact.id}`} fileType={previewArtifact.fileType} />
        </div>
      )}

      <div className="card">
        <h2>Current revision</h2>
        {component.currentRevision ? (
          <div>
            <p>
              <Link href={`/revisions/${component.currentRevision.id}`}>Rev {component.currentRevision.label}</Link>{" "}
              <span className="badge">{component.currentRevision.status}</span>
            </p>
            <p>{component.currentRevision.description}</p>
          </div>
        ) : (
          <p>Sin revisión actual definida.</p>
        )}
      </div>

      <div className="card">
        <h2>Revision history</h2>
        <table>
          <thead>
            <tr>
              <th>Rev</th>
              <th>Status</th>
              <th>Change summary</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {component.revisions.map((r) => (
              <tr key={r.id}>
                <td>
                  <Link href={`/revisions/${r.id}`}>{r.label}</Link>
                </td>
                <td>
                  <span className="badge">{r.status}</span>
                </td>
                <td>{r.changeSummary ?? "—"}</td>
                <td>{r.createdAt.toISOString().slice(0, 10)}</td>
              </tr>
            ))}
            {component.revisions.length === 0 && (
              <tr>
                <td colSpan={4}>Sin revisiones todavía.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Dependencies (esto depende de)</h2>
        <ul>
          {component.dependenciesFrom.map((d) => (
            <li key={d.id}>
              <span className="badge">{d.type}</span> <Link href={`/components/${d.toComponent.id}`}>{d.toComponent.name}</Link>
            </li>
          ))}
          {component.dependenciesFrom.length === 0 && <li>Ninguna registrada.</li>}
        </ul>

        <h2>Dependents (dependen de esto)</h2>
        <ul>
          {component.dependenciesTo.map((d) => (
            <li key={d.id}>
              <span className="badge">{d.type}</span> <Link href={`/components/${d.fromComponent.id}`}>{d.fromComponent.name}</Link>
            </li>
          ))}
          {component.dependenciesTo.length === 0 && <li>Ninguno registrado.</li>}
        </ul>
      </div>

      <div className="card">
        <h2>Documents</h2>
        <ul>
          {documents.map((doc) => (
            <li key={doc.id}>
              {doc.title} <span className="badge">{doc.status}</span>
            </li>
          ))}
          {documents.length === 0 && <li>Ningún documento vinculado.</li>}
        </ul>
      </div>

      <div className="card">
        <h2>Artifacts (revisión actual)</h2>
        <ul>
          {component.currentRevision?.artifacts.map((a) => (
            <li key={a.id}>
              <a href={`/api/artifacts/${a.id}`}>{a.filename}</a> ({a.fileType}, {a.sizeBytes.toString()} bytes)
            </li>
          ))}
          {(!component.currentRevision || component.currentRevision.artifacts.length === 0) && (
            <li>Ningún artifact en la revisión actual.</li>
          )}
        </ul>
      </div>

      <div className="card">
        <h2>Builds</h2>
        <ul>
          {component.buildComponents.map((bc) => (
            <li key={bc.id}>
              <Link href={`/builds/${bc.build.id}`}>{bc.build.code}</Link> usa Rev {bc.revision.label}
            </li>
          ))}
          {component.buildComponents.length === 0 && <li>No usado en ningún build todavía.</li>}
        </ul>
      </div>

      <div className="card">
        <h2>Tests</h2>
        <ul>
          {component.testsAsTarget.map((t) => (
            <li key={t.id}>
              {t.name} <span className="badge">{t.result}</span> — {t.date.toISOString().slice(0, 10)}
            </li>
          ))}
          {component.testsAsTarget.length === 0 && <li>Ningún test registrado.</li>}
        </ul>
      </div>
    </div>
  );
}
