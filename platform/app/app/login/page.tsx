export default function LoginPage({
  searchParams,
}: {
  searchParams: { error?: string };
}) {
  return (
    <div className="card" style={{ maxWidth: 360, margin: "3rem auto" }}>
      <h1>Ingresar</h1>
      {searchParams.error && (
        <p style={{ color: "#e06666" }}>Email o contraseña incorrectos.</p>
      )}
      <form action="/api/auth/login" method="post" style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        <label>
          Email
          <input type="email" name="email" required style={{ width: "100%" }} />
        </label>
        <label>
          Contraseña
          <input type="password" name="password" required style={{ width: "100%" }} />
        </label>
        <button type="submit">Ingresar</button>
      </form>
      <p style={{ fontSize: "0.85rem", opacity: 0.7, marginTop: "1rem" }}>
        Usuario de ejemplo tras <code>npm run seed</code>: admin@argos.local / argos-admin
      </p>
    </div>
  );
}
