import Link from "next/link";
import { globalSearch } from "@/lib/search";

export const dynamic = "force-dynamic";

export default async function SearchPage({ searchParams }: { searchParams: { q?: string } }) {
  const query = searchParams.q ?? "";
  const results = query ? await globalSearch(query) : [];

  return (
    <div>
      <h1>Search</h1>
      <form>
        <input type="text" name="q" defaultValue={query} placeholder="Buscar components, documents..." style={{ width: 320 }} />
        <button type="submit">Buscar</button>
      </form>

      <div className="card">
        {results.map((r) => (
          <div key={`${r.type}-${r.id}`} style={{ marginBottom: "0.75rem" }}>
            <span className="badge">{r.type}</span>{" "}
            <Link href={r.type === "component" ? `/components/${r.id}` : "#"}>{r.title}</Link>
            <p style={{ fontSize: "0.85rem", opacity: 0.8 }}>{r.snippet}</p>
          </div>
        ))}
        {query && results.length === 0 && <p>Sin resultados.</p>}
      </div>
    </div>
  );
}
