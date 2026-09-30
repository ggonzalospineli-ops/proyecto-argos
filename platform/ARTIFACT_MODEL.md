# ARTIFACT_MODEL.md — Fase 4

## Campos (ya definidos en `DATABASE_SCHEMA.md`, tabla `artifacts`)

| Campo | Tipo | Notas |
|---|---|---|
| filename | TEXT | nombre original del archivo subido |
| file_type | TEXT | extensión normalizada, minúscula, sin punto (`step`, `stl`, `3mf`, `pdf`, `png`...) |
| size_bytes | BIGINT | |
| checksum | TEXT | SHA-256 del contenido, calculado server-side al subir |
| storage_key | TEXT | key/ruta dentro del storage abstraído, ej. `revisions/<revision_id>/<uuid>-<filename>` |
| parent entity | — | siempre `revision_id` (NOT NULL) — un Artifact **siempre** cuelga de una Revision, nunca directo de un Component (fuerza a que todo archivo tenga versión explícita) |
| uploaded_by / uploaded_at | — | auditoría mínima |

## Abstracción de storage

Interfaz mínima que la app implementa (Fase 9), para poder swappear
filesystem local (dev) por S3-compatible (prod) sin tocar el resto del
código:

```typescript
interface ArtifactStorage {
  put(key: string, data: Buffer, contentType: string): Promise<void>;
  get(key: string): Promise<Buffer>;
  getSignedUrl(key: string, expiresInSeconds?: number): Promise<string>;
  delete(key: string): Promise<void>;
}
```

- **Dev**: `LocalFilesystemStorage` — escribe bajo
  `platform/app/.data/artifacts/<key>`, gitignored.
- **Prod (futuro)**: `S3CompatibleStorage` (AWS S3, Cloudflare R2, MinIO,
  etc.) implementando la misma interfaz — swap por variable de entorno
  (`ARTIFACT_STORAGE_DRIVER=local|s3`), sin cambios en rutas ni componentes
  de la app.

## Qué NO hace este modelo

- No parsea ni interpreta el contenido del archivo (no hay CAD engine).
- No genera thumbnails automáticamente (post-MVP).
- No versiona el archivo en sí — versionar significa subir un artifact
  nuevo a una Revision nueva, nunca sobreescribir `storage_key` de un
  artifact existente.
