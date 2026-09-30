import Link from "next/link";
import { notFound } from "next/navigation";
import { prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function SystemPage({ params }: { params: { id: string } }) {
  const system = await prisma.system.findUnique({
    where: { id: params.id },
    include: {
      subsystems: true,
      components: true,
      parentSystem: true,
    },
  });

  if (!system) return notFound();

  return (
    <div>
      <p>
        <Link href="/">← Dashboard</Link>
        {system.parentSystem && (
          <>
            {" / "}
            <Link href={`/systems/${system.parentSystem.id}`}>{system.parentSystem.name}</Link>
          </>
        )}
      </p>
      <h1>{system.name}</h1>
      <span className="badge">{system.status}</span>
      <p>{system.description}</p>

      {system.subsystems.length > 0 && (
        <div className="card">
          <h2>Subsystems</h2>
          <ul>
            {system.subsystems.map((s) => (
              <li key={s.id}>
                <Link href={`/systems/${s.id}`}>{s.name}</Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="card">
        <h2>Components</h2>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {system.components.map((c) => (
              <tr key={c.id}>
                <td>
                  <Link href={`/components/${c.id}`}>{c.name}</Link>
                </td>
                <td>{c.type}</td>
                <td>
                  <span className="badge">{c.status}</span>
                </td>
              </tr>
            ))}
            {system.components.length === 0 && (
              <tr>
                <td colSpan={3}>Ningún componente directo en este system.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
