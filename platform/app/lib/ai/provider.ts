import type { ContextFragment } from "./context";

// Llamada al LLM — ver AI_ARCHITECTURE.md. Proveedor configurable por env
// var, sin credenciales hardcodeadas. Si no hay AI_API_KEY, se devuelve un
// error claro en vez de fallar silenciosamente o inventar una respuesta.

const SYSTEM_PROMPT = `Sos el asistente de ingenieria de Argos. Respondes preguntas UNICAMENTE usando la informacion en el contexto provisto a continuacion.

Reglas estrictas:
- Si la respuesta no esta en el contexto, respondes EXACTAMENTE: "Information not defined in the current Argos knowledge base."
- No completes huecos con suposiciones ni conocimiento general sobre drones, ingenieria, o Argos como empresa.
- Toda afirmacion importante debe citar su fuente entre corchetes, ej. [Component: Motor Mount].
- Sos de solo lectura: nunca proponés ejecutar ni confirmás haber ejecutado ninguna modificacion.`;

export class AIProviderNotConfiguredError extends Error {
  constructor() {
    super("AI assistant no configurado: falta AI_API_KEY (ver .env.example).");
  }
}

export async function askLLM(question: string, context: ContextFragment[]): Promise<string> {
  const apiKey = process.env.AI_API_KEY;
  if (!apiKey) {
    throw new AIProviderNotConfiguredError();
  }

  const provider = process.env.AI_PROVIDER ?? "anthropic";
  const model = process.env.AI_MODEL ?? "claude-sonnet-5";

  const contextText = context.length
    ? context.map((f) => `[${f.source}]\n${f.text}`).join("\n\n---\n\n")
    : "(sin resultados para esta pregunta)";

  if (provider === "anthropic") {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model,
        max_tokens: 1024,
        system: SYSTEM_PROMPT,
        messages: [
          {
            role: "user",
            content: `CONTEXTO:\n\n${contextText}\n\nPREGUNTA: ${question}`,
          },
        ],
      }),
    });

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`Error del proveedor de IA (${response.status}): ${body}`);
    }

    const data = (await response.json()) as {
      content: { type: string; text?: string }[];
    };
    const textBlock = data.content.find((b) => b.type === "text");
    return textBlock?.text ?? "Information not defined in the current Argos knowledge base.";
  }

  throw new Error(
    `AI_PROVIDER="${provider}" no implementado. Solo "anthropic" existe en el MVP (ver platform/AI_ARCHITECTURE.md).`
  );
}
