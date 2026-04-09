import { API_BASE } from "@/config";

export async function ingestPDF(file: File, mode: "fast" | "full") {
  const form = new FormData();
  form.append("file", file);
  form.append("mode", mode);

  const res = await fetch(`${API_BASE}/ingest/`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    let errorMessage = "Failed to upload PDF";
    try {
      const errorBody = await res.json();
      errorMessage = errorBody?.detail || errorBody?.message || errorMessage;
    } catch {
      try {
        const errorText = await res.text();
        if (errorText) {
          errorMessage = errorText;
        }
      } catch {
        // Fall back to the default message when the response body is unreadable.
      }
    }
    throw new Error(errorMessage);
  }
  return res.json();
}

export async function askQuestion(sessionId: string, question: string) {
  const res = await fetch(`${API_BASE}/ask/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      thread_id: sessionId,
      question
    }),
    cache: "no-store",
  });

  if (!res.ok) throw new Error("Failed to get answer");
  return res.json();
}
