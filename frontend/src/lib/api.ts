import { API_BASE } from "@/config";

export async function ingestPDF(file: File) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/ingest/`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) throw new Error("Failed to upload PDF");
  return res.json();
}

export async function askQuestion(sessionId: number, question: string) {
  const res = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      question
    }),
    cache: "no-store",
  });

  if (!res.ok) throw new Error("Failed to get answer");
  return res.json();
}
