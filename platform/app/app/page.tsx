import Link from "next/link";
import { prisma } from "@/lib/db";

// Datos en vivo desde Postgres en cada request — nunca prerenderizar
// estaticamente en build time (no hay DATABASE_URL disponible en build).
export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const project = await prisma.project.findFirst({
    where: { name: "ARGOS 1" },
    include: {
      systems: { where: { parentSystemId: null } },
    },
  });

  if (!project) {
    return (
      <div className="card">
        <h1>Argos Engineering Platform</h1>
        <p>
          No existe todavía el proyecto <code>ARGOS 1</code>. Corré{" "}
          <code>npm run seed</code> para crearlo (ver platform/app/README.md).
        </p>
      </div>
    );
  }

  const [componentCount, revisionCount, buildCount, testCount, openTests] = await Promise.all([
    prisma.component.count({ where: { projectId: project.id } }),
    prisma.revision.count({ where: { component: { projectId: project.id } } }),
    prisma.build.count({ where: { projectId: project.id } }),
    prisma.test.count({ where: { targetComponent: { projectId: project.id } } }),
    prisma.test.findMany({
      where: { targetComponent: { projectId: project.id } },
      orderBy: { date: "desc" },
      take: 5,
      include: { targetComponent: { select: { name: true, id: true } } },
    }),
  ]);

  const recentRevisions = await prisma.revision.findMany({
    where: { component: { projectId: project.id } },
    orderBy: { createdAt: "desc" },
    take: 5,
    include: { component: { select: { name: true, id: true } } },
  });

  const activeBuilds = await prisma.build.findMany({
    where: { projectId: project.id, status: { in: ["PLANNED", "ASSEMBLED", "TESTING"] } },
    take: 5,
  });

  return (
    <div>
      <h1>{project.name}</h1>
      <p>{project.description}</p>

      <div className="card" style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem" }}>
        <div>
          <div style={{ fontSize: "1.75rem" }}>{project.systems.length}</div>
          <div>Systems</div>
        </div>
        <div>
          <div style={{ fontSize: "1.75rem" }}>{componentCount}</div>
          <div>Components</div>
        </div>
        <div>
          <div style={{ fontSize: "1.75rem" }}>{revisionCount}</div>
          <div>Revisions</div>
        </div>
        <div>
          <div style={{ fontSize: "1.75rem" }}>{buildCount}</div>
          <div>Builds</div>
        </div>
      </div>

      <div className="card">
        <h2>Systems</h2>
        <ul>
          {project.systems.map((system) => (
            <li key={system.id}>
              <Link href={`/systems/${system.id}`}>{system.name}</Link>{" "}
              <span className="badge">{system.status}</span>
            </li>
          ))}
          {project.systems.length === 0 && <li>Ningún system cargado todavía.</li>}
        </ul>
      </div>

      <div className="card">
        <h2>Recent revisions</h2>
        <table>
          <tbody>
            {recentRevisions.map((r) => (
              <tr key={r.id}>
                <td>
                  <Link href={`/components/${r.component.id}`}>{r.component.name}</Link>
                </td>
                <td>Rev {r.label}</td>
                <td>
                  <span className="badge">{r.status}</span>
                </td>
                <td>{r.createdAt.toISOString().slice(0, 10)}</td>
              </tr>
            ))}
            {recentRevisions.length === 0 && (
              <tr>
                <td>Ninguna revisión todavía.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Active builds ({buildCount} total)</h2>
        <ul>
          {activeBuilds.map((b) => (
            <li key={b.id}>
              <Link href={`/builds/${b.id}`}>{b.code}</Link> <span className="badge">{b.status}</span>
            </li>
          ))}
          {activeBuilds.length === 0 && <li>Ningún build activo.</li>}
        </ul>
      </div>

      <div className="card">
        <h2>Recent tests ({testCount} total)</h2>
        <ul>
          {openTests.map((t) => (
            <li key={t.id}>
              {t.name} — <Link href={`/components/${t.targetComponent.id}`}>{t.targetComponent.name}</Link>{" "}
              <span className="badge">{t.result}</span>
            </li>
          ))}
          {openTests.length === 0 && <li>Ningún test registrado.</li>}
        </ul>
      </div>
    </div>
  );
}
