/**
 * Backend API client. Sends question and conversation_history so the LLM
 * receives the last N messages and can remember the session (e.g. user's name).
 */
const MAX_CONTEXT_MESSAGES = 20;

export function query(apiBase, question, conversationHistory = [], sessionId = null) {
  const history = Array.isArray(conversationHistory)
    ? conversationHistory.slice(-MAX_CONTEXT_MESSAGES).map((m) => ({
        role: m.role,
        content: typeof m.content === "string" ? m.content : String(m.content ?? ""),
      }))
    : [];
  const body = { question, conversation_history: history };
  if (sessionId) body.session_id = sessionId;
  return fetch(apiBase + "/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then(async (res) => {
    if (!res.ok) {
      let msg = "Request failed: " + res.status;
      try {
        const d = await res.json();
        if (d && (d.detail != null)) msg = typeof d.detail === "string" ? d.detail : JSON.stringify(d.detail);
      } catch (_) {}
      throw new Error(msg);
    }
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

/** Sessions: stored in PostgreSQL, not browser memory */
export function listSessions(apiBase) {
  const url = (apiBase || "").replace(/\/$/, "") + "/api/sessions";
  return fetch(url).then(async (res) => {
    if (!res.ok) throw new Error("Failed to list sessions: " + res.status);
    return res.json();
  });
}

export function createSession(apiBase, title = "New chat") {
  const url = (apiBase || "").replace(/\/$/, "") + "/api/sessions?title=" + encodeURIComponent(title);
  return fetch(url, { method: "POST" }).then(async (res) => {
    if (!res.ok) {
      let msg = res.status + " " + (res.statusText || "");
      try {
        const d = await res.json();
        if (d && (d.detail || d.message)) msg = typeof d.detail === "string" ? d.detail : d.message || msg;
      } catch (_) {}
      throw new Error(msg);
    }
    return res.json();
  });
}

export function getSession(apiBase, sessionId) {
  return fetch(apiBase + "/api/sessions/" + encodeURIComponent(sessionId)).then((res) => {
    if (!res.ok) throw new Error("Failed to load session: " + res.status);
    return res.json();
  });
}

export function deleteSession(apiBase, sessionId) {
  return fetch(apiBase + "/api/sessions/" + encodeURIComponent(sessionId), {
    method: "DELETE",
  }).then((res) => {
    if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || res.status); });
    return res.json();
  });
}
