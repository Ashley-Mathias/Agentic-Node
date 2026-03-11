/**
 * Backend API client. Sends question and conversation_history so the LLM
 * receives the last N messages and can remember the session (e.g. user's name).
 */
const MAX_CONTEXT_MESSAGES = 20;

export function query(apiBase, question, conversationHistory = []) {
  const history = Array.isArray(conversationHistory)
    ? conversationHistory.slice(-MAX_CONTEXT_MESSAGES).map((m) => ({
        role: m.role,
        content: typeof m.content === "string" ? m.content : String(m.content ?? ""),
      }))
    : [];
  return fetch(apiBase + "/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, conversation_history: history }),
  }).then((res) => {
    if (!res.ok) throw new Error("Request failed: " + res.status);
    return res.json();
  });
}

export function upload(apiBase, file) {
  const formData = new FormData();
  formData.append("file", file);
  return fetch(apiBase + "/api/upload", {
    method: "POST",
    body: formData,
  }).then((res) => {
    if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || res.status); });
    return res.json();
  });
}
