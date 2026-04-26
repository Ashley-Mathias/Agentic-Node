// frontend/js/ — client-side chat application (sessions, API, UI).
/**
 * App entry: chat sessions and memory in PostgreSQL; no browser storage.
 * Sidebar shows all sessions; delete in UI deletes from DB synchronously.
 */
import { getApiBase } from "./config.js";
import * as api from "./api.js";
import * as chatUI from "./chatUI.js";
import { initInputBar } from "./inputBar.js";
import { initDownloadHandlers } from "./messageRenderer.js";

console.log("[App] app.js module loaded");

let messagesEl, messageInput, sendBtn, fileInput, sessionListEl;
/** Current session id (from PostgreSQL). Null = no session or new chat not yet sent. */
let currentSessionId = null;
/** In-memory only for current chat (for API context); loaded from DB when switching session. */
let conversationHistory = [];
/** Cached session list so we can optimistically add the new session when user clicks "New chat". */
let sessionsCache = [];

function init() {
  console.log("[App] init() called");
  messagesEl = document.getElementById("messages");
  messageInput = document.getElementById("messageInput");
  sendBtn = document.getElementById("sendBtn");
  fileInput = document.getElementById("fileInput");
  sessionListEl = document.getElementById("sessionList");

  if (!messagesEl) {
    console.warn("[App] messages element not found, aborting init");
    return;
  }
  console.log("[App] DOM elements found, setting up UI");
  if (typeof window !== "undefined" && window.__currentSessionId)
    currentSessionId = window.__currentSessionId;
  chatUI.initChatUI(messagesEl);
  initDownloadHandlers(messagesEl);

function renderSessions(sessions) {
  if (!sessionListEl) return;
  sessionListEl.innerHTML = "";
  for (const s of sessions) {
    const wrap = document.createElement("div");
    wrap.className = "sidebar-session-item" + (s.id === currentSessionId ? " active" : "");
    wrap.dataset.sessionId = s.id;
    const title = document.createElement("span");
    title.className = "sidebar-session-item-title";
    title.textContent = s.title || "New chat";
    wrap.appendChild(title);
    const delBtn = document.createElement("button");
    delBtn.type = "button";
    delBtn.className = "sidebar-session-item-delete";
    delBtn.setAttribute("aria-label", "Delete chat");
    delBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>';
    delBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteSession(s.id);
    });
    wrap.appendChild(delBtn);
    wrap.addEventListener("click", () => selectSession(s.id));
    sessionListEl.appendChild(wrap);
  }
}

function refreshSessions() {
  const apiBase = getApiBase();
  api.listSessions(apiBase)
    .then((data) => {
      sessionsCache = data.sessions || [];
      renderSessions(sessionsCache);
    })
    .catch(() => {
      if (sessionsCache.length === 0) renderSessions([]);
    });
}

function selectSession(sessionId) {
  const apiBase = getApiBase();
  api.getSession(apiBase, sessionId)
    .then((session) => {
      currentSessionId = session.id;
      conversationHistory = (session.messages || []).map((m) => ({ role: m.role, content: m.content }));
      chatUI.loadMessages(session.messages || []);
      refreshSessions();
      document.getElementById("appShell").classList.remove("sidebar-open");
    })
    .catch(() => {});
}

function deleteSession(sessionId) {
  const apiBase = getApiBase();
  api.deleteSession(apiBase, sessionId)
    .then(() => {
      if (currentSessionId === sessionId) {
        currentSessionId = null;
        conversationHistory = [];
        chatUI.resetToWelcome();
      }
      refreshSessions();
    })
    .catch(() => {});
}

  // New chat is handled by the inline script in index.html so we don't attach a second
  // listener here (which would create two sessions per click when both run).

function sendQuery(question) {
  const apiBase = getApiBase();
  if (typeof window !== "undefined" && window.__currentSessionId)
    currentSessionId = currentSessionId || window.__currentSessionId;
  const ensureSession = !currentSessionId
    ? api.createSession(apiBase, "New chat").then((s) => { currentSessionId = s.id; if (window.__currentSessionId !== s.id) window.__currentSessionId = s.id; refreshSessions(); return s.id; })
    : Promise.resolve(currentSessionId);

  chatUI.addUserMessage(question);
  const loadingEl = chatUI.addLoadingMessage();
  sendBtn.disabled = true;
  conversationHistory.push({ role: "user", content: question });

  ensureSession.then((sid) => {
    api.query(apiBase, question, conversationHistory, sid)
      .then((data) => {
        chatUI.replaceLoadingWithResponse(loadingEl, data);
        const summary = (data && data.summary) ? data.summary : "";
        conversationHistory.push({ role: "assistant", content: summary });
      })
      .catch((err) => {
        chatUI.replaceLoadingWithResponse(loadingEl, { error: err.message, summary: "" });
        conversationHistory.push({ role: "assistant", content: "(error)" });
      })
      .finally(() => {
        if (conversationHistory.length > 20) conversationHistory.splice(0, conversationHistory.length - 20);
        sendBtn.disabled = false;
        refreshSessions();
      });
  }).catch((err) => {
    const detail =
      err && err.message
        ? err.message
        : "Network or server error. Check API_BASE (Railway URL), GitHub BACKEND_URL secret, and that the backend is running.";
    chatUI.replaceLoadingWithResponse(loadingEl, { error: "Could not create session: " + detail, summary: "" });
    conversationHistory.pop();
    sendBtn.disabled = false;
  });
}

function handleUpload(file) {
  const apiBase = getApiBase();
  chatUI.addUserMessage("Uploaded: " + file.name);
  const loadingEl = chatUI.addLoadingMessage();
  sendBtn.disabled = true;

  api.upload(apiBase, file)
    .then((data) => {
      const msg = data.message || "Uploaded " + data.chunks_stored + " chunks from " + data.filename + ".";
      chatUI.replaceLoadingWithResponse(loadingEl, { summary: msg });
    })
    .catch((err) => chatUI.replaceLoadingWithResponse(loadingEl, { error: err.message, summary: "" }))
    .finally(() => {
      sendBtn.disabled = false;
      if (fileInput) fileInput.value = "";
    });
}

  initInputBar({
    messageInput,
    sendBtn,
    fileInput,
    onSend: sendQuery,
    onUpload: handleUpload,
  });

  refreshSessions();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
