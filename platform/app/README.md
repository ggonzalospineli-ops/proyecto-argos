# Argos Engineering Platform — app (Fase 9 MVP)

Implementación de código del MVP descrito en `platform/` (ver
`../SUMMARY.md` para el índice completo del trabajo de diseño). Next.js
(App Router, TypeScript) + PostgreSQL vía Prisma.

## Alcance implementado

- Auth por credenciales (roles ADMIN/MEMBER/VIEWER), sesión por cookie
  firmada — `lib/auth.ts`.
- Schema Prisma reflejando `../DATABASE_SCHEMA.md` (entidades MVP).
- Páginas de lectura: Dashboard, System Explorer, Component Page
  (con historial de revisiones, dependencias/dependientes, documentos,
  artifacts, builds, tests, y preview 3D de STL), Revision Page, Build
  Page, Search (full-text Postgres), AI Assistant (chat read-only).
- Storage de artifacts abstraído (`lib/storage.ts`), driver `local` para
  dev.
- AI assistant read-only (`lib/ai/`, `app/api/ai/ask/route.ts`) —
  proveedor Anthropic vía `AI_API_KEY`, grounding estricto.
- Seed (`prisma/seed.ts`): usuario admin + proyecto `ARGOS 1` real
  (vacío) + un puñado de registros `[EJEMPLO]` para poder navegar la UI.

## No implementado en esta pasada (ver `../PHASE_9_REPORT.md`)

- UI de creación/edición (formularios para crear Component, subir
  Artifact, crear Build, registrar Test, editar Document). El modelo de
  datos y las páginas de lectura/navegación están completas; el CRUD de
  escritura queda como siguiente iteración de código, no de diseño.
- Preview 3D de 3MF (solo STL está cableado en `components/Viewer3D.tsx`).
- Driver de storage S3 (interfaz lista, solo implementado `local`).

## Cómo correr

```bash
cd platform/app
cp .env.example .env     # completar DATABASE_URL y SESSION_SECRET como minimo
npm install
npm run prisma:generate
npm run prisma:migrate    # requiere una base PostgreSQL disponible en DATABASE_URL
npm run seed
npm run dev
```

Login de ejemplo tras el seed: `admin@argos.local` / `argos-admin`.

Para el AI Assistant, completar `AI_API_KEY` en `.env` (proveedor
Anthropic). Sin esa variable, el endpoint responde 503 con un mensaje
claro en vez de fallar silenciosamente.

## Notas de implementación relevantes

- Búsqueda full-text usa `to_tsvector`/`plainto_tsquery` vía SQL crudo
  (`lib/search.ts`, `lib/ai/context.ts`) en vez de una columna generada
  `search_vector`, para no depender de una migración de trigger SQL
  fuera de lo que Prisma expresa nativamente — ver
  `../PHASE_9_REPORT.md` para el detalle de este trade-off.
