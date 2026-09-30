import type { Metadata } from "next";
import Link from "next/link";
import { getCurrentUser } from "@/lib/auth";
import "./globals.css";

export const metadata: Metadata = {
  title: "Argos Engineering Platform",
  description: "Plataforma de gestion de ingenieria para Argos 1 (MVP)",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser().catch(() => null);

  return (
    <html lang="es">
      <body>
        <nav>
          <Link href="/">Dashboard</Link>
          <Link href="/search">Search</Link>
          <Link href="/ai">AI Assistant</Link>
          <div style={{ marginLeft: "auto" }}>
            {user ? (
              <span>
                {user.name} ({user.role}){" "}
                <form action="/api/auth/logout" method="post" style={{ display: "inline" }}>
                  <button type="submit">Salir</button>
                </form>
              </span>
            ) : (
              <Link href="/login">Ingresar</Link>
            )}
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
