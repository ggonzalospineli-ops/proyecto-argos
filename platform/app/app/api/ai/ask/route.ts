import { NextRequest, NextResponse } from "next/server";
import { getCurrentUser } from "@/lib/auth";
import { buildContext } from "@/lib/ai/context";
import { askLLM, AIProviderNotConfiguredError } from "@/lib/ai/provider";

// Endpoint READ-ONLY del AI assistant — ver AI_ARCHITECTURE.md.
// Nunca ejecuta mutaciones; solo arma contexto (SELECT) y llama al LLM.

export async function POST(req: NextRequest) {
  const user = await getCurrentUser();
  if (!user) {
    return NextResponse.json({ error: "No autenticado." }, { status: 401 });
  }

  const body = (await req.json()) as { question?: string };
  const question = body.question?.trim();
  if (!question) {
    return NextResponse.json({ error: "Falta 'question'." }, { status: 400 });
  }

  const context = await buildContext(question);

  try {
    const answer = await askLLM(question, context);
    return NextResponse.json({
      answer,
      sources: context.map((f) => f.source),
    });
  } catch (err) {
    if (err instanceof AIProviderNotConfiguredError) {
      return NextResponse.json({ error: err.message }, { status: 503 });
    }
    const message = err instanceof Error ? err.message : "Error desconocido";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
