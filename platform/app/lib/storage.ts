import { createHash } from "crypto";
import { mkdir, readFile, writeFile, unlink } from "fs/promises";
import path from "path";

// Interfaz abstracta de storage de artifacts — ver ARTIFACT_MODEL.md.
// Implementacion "local" para dev; "s3" queda documentada como el
// siguiente driver a implementar (mismo contrato), no construida todavia.

export interface ArtifactStorage {
  put(key: string, data: Buffer): Promise<void>;
  get(key: string): Promise<Buffer>;
  delete(key: string): Promise<void>;
}

class LocalFilesystemStorage implements ArtifactStorage {
  constructor(private readonly root: string) {}

  private resolve(key: string): string {
    const safeKey = key.replace(/\.\./g, "");
    return path.join(this.root, safeKey);
  }

  async put(key: string, data: Buffer): Promise<void> {
    const filePath = this.resolve(key);
    await mkdir(path.dirname(filePath), { recursive: true });
    await writeFile(filePath, data);
  }

  async get(key: string): Promise<Buffer> {
    return readFile(this.resolve(key));
  }

  async delete(key: string): Promise<void> {
    await unlink(this.resolve(key));
  }
}

let storageInstance: ArtifactStorage | null = null;

export function getArtifactStorage(): ArtifactStorage {
  if (storageInstance) return storageInstance;

  const driver = process.env.ARTIFACT_STORAGE_DRIVER ?? "local";
  if (driver === "local") {
    const root = process.env.ARTIFACT_STORAGE_LOCAL_PATH ?? ".data/artifacts";
    storageInstance = new LocalFilesystemStorage(path.resolve(process.cwd(), root));
    return storageInstance;
  }

  throw new Error(
    `ARTIFACT_STORAGE_DRIVER="${driver}" no implementado. Solo "local" existe en el MVP (ver platform/ARTIFACT_MODEL.md).`
  );
}

export function checksumOf(data: Buffer): string {
  return createHash("sha256").update(data).digest("hex");
}

export function buildStorageKey(revisionId: string, filename: string): string {
  const safeName = filename.replace(/[^a-zA-Z0-9._-]/g, "_");
  return `revisions/${revisionId}/${Date.now()}-${safeName}`;
}
