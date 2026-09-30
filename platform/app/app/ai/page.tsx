"use client";

import { useState } from "react";

interface Answer {
  question: string;
  answer?: string;
  sources?: string[];
  error?: string;
}

export default function AIAssistantPage() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<Answer[]>([]);
  const [loading, setLoading] = useState(false);

  async function ask(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    const q = question;
    setQuestion("");
    try {
      const res = await fetch("/api/ai/ask", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      setHistory((h) => [...h, { question: q, answer: data.answer, sources: data.sources, error: data.error }]);
    } catch (err) {
      setHistory((h) => [...h, { question: q, error: "Error de red." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1>AI Assistant</h1>
      <p style={{ opacity: 0.8 }}>
        Solo lectura. Responde con lo que existe en la base de conocimiento de Argos, citando su fuente. Si no hay
        información, lo dice explícitamente en vez de inventar.
      </p>

      <div className="card">
        {history.map((h, i) => (
          <div key={i} style={{ marginBottom: "1.25rem" }}>
            <p>
              <strong>Q:</strong> {h.question}
            </p>
            {h.error ? (
              <p style={{ color: "#e06666" }}>{h.error}</p>
            ) : (
              <>
                <p>
                  <strong>A:</strong> {h.answer}
                </p>
                {h.sources && h.sources.length > 0 && (
                  <p style={{ fontSize: "0.8rem", opacity: 0.7 }}>Fuentes: {h.sources.join(" · ")}</p>
                )}
              </>
            )}
          </div>
        ))}
        {history.length === 0 && <p>Sin preguntas todavía.</p>}
      </div>

      <form onSubmit={ask} style={{ display: "flex", gap: "0.5rem" }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ej: ¿Qué componentes forman el Airframe?"
          style={{ flex: 1 }}
        />
        <button type="submit" disabled={loading}>
          {loading ? "..." : "Preguntar"}
        </button>
      </form>
    </div>
  );
}
