# MIGRATION_PLAN.md — Fase 10

## Qué información real existe hoy para cargar

Muy poca, según `CURRENT_COMPONENTS.md` (Fase 0):

| Dato | Existe? | Dónde |
|---|---|---|
| Proyecto `ARGOS 1` | Sí, como concepto de negocio | `empresaquevendearmasproyecto-2028.html` |
| Componentes de hardware reales (frame, motores, cámaras, etc.) | No — solo menciones textuales, sin specs, CAD, ni IDs | HTML |
| Software de visión (`vision/`) | **Sí, código real** | `vision/` (repo aparte, en desarrollo por otro agente) |
| CAD real | No existe ningún archivo CAD en el repo | — |
| Documentación técnica estructurada | No — solo el plan de negocio en HTML | — |
| Builds/prototipos físicos | Desconocido si existen (ver `OPEN_QUESTIONS.md`) | — |
| Tests reales | Ninguno documentado | — |

**Conclusión**: hoy no hay un dataset real de Argos para migrar más allá
de reconocer que `vision/` existe como software real. No se fabrica un
dataset "real" para llenar este vacío (regla explícita del usuario).

## Qué le falta pedir al usuario para poblar la plataforma de verdad

1. **Inventario real de hardware**: lista de piezas/ensambles reales
   (aunque sea informal — fotos, notas, una planilla) para crear los
   primeros `System`/`Component` reales.
2. **CAD real**: al menos un archivo STEP/STL/3MF de una pieza real, para
   probar el flujo completo de Artifact + preview 3D con datos genuinos.
3. **Decisión sobre `vision/`**: ¿se integra como `Component` de tipo
   `SOFTWARE` dentro de `ARGOS 1` (versionado junto con el resto), o
   sigue siendo un repo/carpeta independiente fuera de este modelo? (Ver
   `OPEN_QUESTIONS.md` — sigue sin resolver.)
4. **Documentación existente** (si la hay fuera de este repo): notas de
   diseño, decisiones tomadas, resultados de pruebas de campo — para
   cargarlas como `Document` reales en vez de placeholders.
5. **Confirmación de alcance**: si `SENTINEL-1` es un proyecto separado o
   parte de `ARGOS 1` (afecta directamente cómo se estructura el primer
   `Project` real más allá del único que existe hoy).
6. **Estado real del equipo/roles**: quién es `ADMIN` vs `MEMBER` vs
   `VIEWER` en la práctica, para el seed de usuarios reales (reemplazando
   el usuario `admin@argos.local` de ejemplo).

## Plan de migración, una vez que exista lo anterior

1. Reemplazar el seed de ejemplo (`prisma/seed.ts`) por un script de
   carga real, o cargar manualmente vía la futura UI de escritura
   (ver `PHASE_9_REPORT.md`, "Recommended actions").
2. Empezar por UN component real completo (siguiendo el "MVP Demo
   Scenario" del primer bloque del usuario: crear componente, asignarlo
   a un system, subir CAD, crear Rev A, documentar, declarar
   dependencias, crear Rev B con un cambio real, crear un Build que lo
   use, registrar un test) antes de cargar el resto — exactamente el
   caso de prueba que `TRACEABILITY_EXAMPLE.md` simuló con datos
   ficticios.
3. Validar que el AI assistant responde correctamente sobre ESE dato
   real antes de seguir cargando más.
4. Recién después, escalar a más componentes.

## Qué NO hacer

- No fabricar specs de hardware, capacidades de vuelo, ni resultados de
  tests para "completar" el dataset — todo hueco se deja como
  `[TO BE DEFINED]` hasta que el usuario lo provea.
