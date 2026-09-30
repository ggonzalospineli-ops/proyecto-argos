import Link from "next/link";
import { notFound } from "next/navigation";
import { prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function BuildPage({ params }: { params: { id: string } }) {
  const build = await prisma.build.findUnique({
    where: { id: params.id },
    include: {
      buildComponents: { include: { component: true, revision: true } },
      tests: { include: { targetComponent: true } },
    },
  });

  if (!build) return notFound();

  const documents = await prisma.document.findMany({
    where: { entityType: "BUILD", entityId: build.id },
  });

  return (
    <div>
      <p>
        <Link href="/">← Dashboard</Link>
      </p>
      <h1>{build.code}</h1>
      <span className="badge">{build.status}</span>
      <p>{build.description}</p>

      <div className="card">
        <h2>Components / Revisions</h2>
        <table>
          <thead>
            <tr>
              <th>Component</th>
              <th>Revision</th>
            </tr>
          </thead>
          <tbody>
            {build.buildComponents.map((bc) => (
              <tr key={bc.id}>
                <td>
                  <Link href={`/components/${bc.component.id}`}>{bc.component.name}</Link>
                </td>
                <td>
                  <Link href={`/revisions/${bc.revision.id}`}>Rev {bc.revision.label}</Link>
                </td>
              </tr>
            ))}
            {build.buildComponents.length === 0 && (
              <tr>
                <td colSpan={2}>Sin componentes definidos todavía.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Tests</h2>
        <ul>
          {build.tests.map((t) => (
            <li key={t.id}>
              {t.name} — {t.targetComponent.name} <span className="badge">{t.result}</span>
            </li>
          ))}
          {build.tests.length === 0 && <li>Ningún test registrado para este build.</li>}
        </ul>
      </div>

      <div className="card">
        <h2>Issues / Notes</h2>
        <ul>
          {documents.map((d) => (
            <li key={d.id}>{d.title}</li>
          ))}
          {documents.length === 0 && <li>Sin documentos/issues vinculados.</li>}
        </ul>
      </div>
    </div>
  );
}
