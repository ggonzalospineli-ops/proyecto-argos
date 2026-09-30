# PHASE_9_REPORT.md

**Objective**: Convertir el diseño de Fases 1-8 en una aplicación
funcional mínima (Next.js + PostgreSQL/Prisma), código real en
`platform/app/`.

**Completed**
- App Next.js 14 (App Router, TypeScript) en `platform/app/`.
- `prisma/schema.prisma` — implementación 1:1 de las 12 tablas MVP de
  `DATABASE_SCHEMA.md` (users, projects, systems, components, revisions,
  artifacts, documents, component_dependencies, bom_lines, builds,
  build_components, tests).
- Auth por credenciales propia (`lib/auth.ts`): scrypt nativo de Node
  para hash de password (sin dependencia externa tipo bcrypt), cookie de
  sesión firmada con HMAC-SHA256, roles ADMIN/MEMBER/VIEWER.
- Storage de artifacts abstraído (`lib/storage.ts`): interfaz
  `ArtifactStorage`, implementación `local` (filesystem, dev) — driver
  `s3` documentado pero no implementado, exactamente como pide
  `ARTIFACT_MODEL.md`.
- Búsqueda full-text (`lib/search.ts`) vía `to_tsvector`/
  `plainto_tsquery` en SQL crudo (`$queryRaw`), sobre `components` y
  `documents`.
- AI Assistant read-only completo: `lib/ai/context.ts` (arma STRUCTURED +
  DOCUMENT CONTEXT con heurística de nombre + fallback full-text, tal
  como diseña `AI_CONTEXT_STRATEGY.md`), `lib/ai/provider.ts` (llamada a
  la API de Anthropic vía `fetch`, modelo configurable por
  `AI_MODEL`/`AI_API_KEY`, sin credenciales hardcodeadas, error explícito
  si no está configurado), `app/api/ai/ask/route.ts` (endpoint,
  autenticado, solo `SELECT`), `app/ai/page.tsx` (chat UI con source
  attribution visible).
- Páginas: Dashboard (`app/page.tsx`), System Explorer
  (`app/systems/[id]`), Component Page (`app/components/[id]` — incluye
  current revision, historial de revisiones, dependencies/dependents,
  documents, artifacts, builds, tests, y el 3D viewer), Revision Page,
  Build Page, Search, AI Assistant, Login.
- 3D Viewer PoC (`components/Viewer3D.tsx`): react-three-fiber +
  STLLoader, rotate/pan/zoom vía `OrbitControls`. Solo STL está cableado
  (3MF queda pendiente — ver "Not completed").
- `prisma/seed.ts`: crea el usuario admin, el proyecto real `ARGOS 1`
  (vacío de componentes reales) y un set mínimo de registros
  explícitamente sufijados `[EJEMPLO]` (1 system, 1 component, 1
  revision, 1 document, 1 build, 1 test) para poder navegar toda la UI
  sin fabricar datos reales de Argos.
- `README.md` con instrucciones de instalación/uso.

**Verificación de compilación (sin base de datos disponible en este
entorno)**
- `npm install`: OK (113 paquetes).
- `npx prisma generate`: OK.
- `npx tsc --noEmit`: OK, sin errores (tras corregir un error de tipos en
  `app/api/artifacts/[id]/route.ts`: `Buffer` no es asignable a
  `BodyInit`, resuelto envolviendo con `new Uint8Array(data)`).
- `npx next build`: OK — todas las rutas compilan; se agregó
  `export const dynamic = "force-dynamic"` a las páginas que consultan
  Prisma, porque Next intentaba prerenderizarlas estáticamente en build
  time y fallaba por falta de `DATABASE_URL` (esperable: no hay Postgres
  disponible en este entorno). Con ese flag, el build termina limpio y
  las páginas quedan correctamente marcadas como server-rendered on
  demand, que es el comportamiento correcto para datos en vivo.

**No se pudo probar** (requiere PostgreSQL real, no disponible en este
entorno): `prisma migrate dev`, `npm run seed`, y el comportamiento en
runtime de cualquier página o del AI assistant. El código compila y el
build de producción pasa, pero **no hay verificación end-to-end contra
una base de datos real** — es la limitación más importante a tener en
cuenta antes de considerar esto "probado".

**Not completed**
- **UI de escritura/mutación**: no hay formularios para crear Component,
  System, subir Artifact, crear Build, registrar Test, ni editar
  Document desde la interfaz. El schema y las páginas de lectura están
  completos; todo lo que hoy es de solo lectura tendría que poblarse vía
  `seed.ts`/Prisma Studio/SQL directo hasta que se construya esa capa.
  Esto es la brecha más grande entre "modelo funcional" y "plataforma
  usable por el equipo" — priorizarla es la recomendación más importante
  de este reporte.
- Preview 3D de 3MF (solo STL implementado en `Viewer3D.tsx`).
- Driver de storage S3-compatible (interfaz lista, no implementado).
- Middleware de protección de rutas a nivel global: cada página no
  fuerza explícitamente redirect a `/login` si no hay sesión (el layout
  muestra el link de "Ingresar" pero no bloquea la vista de las páginas
  de datos). El endpoint de IA sí valida autenticación. Antes de
  cualquier uso con datos sensibles reales, hay que cerrar este gap.

**Decisions**
- Auth casera (HMAC + scrypt) en vez de NextAuth/Auth.js, para minimizar
  superficie de dependencias externas no verificables en este entorno
  sin red persistente — trade-off consciente de "menos robusto pero
  totalmente auditable en ~120 líneas de código".
- `force-dynamic` en todas las páginas que leen de Postgres, en vez de
  Static Site Generation — correcto para datos que cambian
  constantemente, y evita que el build dependa de tener una base de
  datos disponible en build time.

**Unknowns**
- Ninguno nuevo de producto — los unknowns siguen siendo los de datos
  reales (Fase 0/10).

**Risks**
- Sin UI de escritura, el "MVP" hoy es navegable pero no operable por el
  equipo sin tocar la base de datos directamente — alto riesgo de que se
  perciba como "no funciona" si se muestra sin aclarar este alcance.
- Sin protección de rutas a nivel de página, cualquiera con la URL puede
  ver datos aunque no esté logueado (aunque hoy solo hay datos
  `[EJEMPLO]`) — debe resolverse antes de cargar cualquier dato real
  sensible.
- No hay tests automatizados (unit/integration) — toda la verificación
  hecha acá es de compilación, no de comportamiento.

**Next phase**: Fase 10 — Validación con Argos real.

**Recommended actions**
1. Antes de nada: construir la UI de escritura mínima (crear Component,
   subir Artifact a una Revision, crear Build, registrar Test) — sin
   esto, la plataforma no reemplaza today's proceso manual del equipo.
2. Agregar guard de sesión a nivel de layout/middleware.
3. Conseguir una instancia de Postgres (local Docker o managed) y correr
   `prisma migrate dev` + `npm run seed` + `npm run dev` para la primera
   verificación end-to-end real, incluyendo login y el AI assistant con
   una `AI_API_KEY` real.
