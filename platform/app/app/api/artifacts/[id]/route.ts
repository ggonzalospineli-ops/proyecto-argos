import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import { getArtifactStorage } from "@/lib/storage";

export async function GET(_req: NextRequest, { params }: { params: { id: string } }) {
  const artifact = await prisma.artifact.findUnique({ where: { id: params.id } });
  if (!artifact) {
    return NextResponse.json({ error: "Artifact no encontrado" }, { status: 404 });
  }

  const storage = getArtifactStorage();
  const data = await storage.get(artifact.storageKey);

  return new NextResponse(new Uint8Array(data), {
    headers: {
      "content-type": "application/octet-stream",
      "content-disposition": `inline; filename="${artifact.filename}"`,
    },
  });
}
