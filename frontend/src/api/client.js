import { API_BASE_URL } from "../config";

async function readError(res) {
  const data = await res.json().catch(() => ({}));
  return typeof data.detail === "string" ? data.detail : `Request failed (${res.status})`;
}

export async function getHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

/**
 * Ask a question and receive the answer as it is written.
 * The server sends one JSON event per line:
 *   {type:"status", stage}  {type:"sources", found, sources}
 *   {type:"token", text}    {type:"done"}   {type:"error", message}
 */
export async function askStream(question, { onEvent, signal }) {
  const res = await fetch(`${API_BASE_URL}/ask/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
    signal,
  });
  if (!res.ok) throw new Error(await readError(res));

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop(); // keep a half-received line for the next round
    for (const line of lines) {
      if (line.trim()) onEvent(JSON.parse(line));
    }
  }
  if (buffer.trim()) onEvent(JSON.parse(buffer));
}