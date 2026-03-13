/**
 * Chat message list: append user/bot bubbles, loading state, replace with response.
 */
import { buildBotContentHtml } from "./messageRenderer.js";

let messagesEl = null;

export function initChatUI(containerEl) {
  messagesEl = containerEl;
}

function scrollToBottom() {
  if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addMessage(role, contentHtml) {
  if (!messagesEl) return null;
  const wrap = document.createElement("div");
  wrap.className = "message message-" + role;
  wrap.setAttribute("data-testid", role === "user" ? "message-user" : "message-bot");
  wrap.innerHTML = '<div class="bubble">' + contentHtml + "</div>";
  messagesEl.appendChild(wrap);
  scrollToBottom();
  return wrap;
}

export function addUserMessage(text) {
  const div = document.createElement("div");
  div.textContent = text;
  const escaped = div.innerHTML;
  return addMessage("user", "<p>" + escaped + "</p>");
}

export function addLoadingMessage() {
  const wrap = addMessage("bot", "Thinking");
  if (wrap) wrap.classList.add("message-loading");
  return wrap;
}

export function replaceLoadingWithResponse(loadingEl, data) {
  if (!loadingEl) return;
  loadingEl.classList.remove("message-loading");
  const bubble = loadingEl.querySelector(".bubble");
  if (bubble) bubble.innerHTML = buildBotContentHtml(data);
  scrollToBottom();
}

/** Show an error message in the chat (e.g. backend unreachable). */
export function showError(message) {
  if (!messagesEl) return;
  addMessage("bot", buildBotContentHtml({ error: message, summary: "" }));
}

/**
 * Clear all messages except the welcome message (for "New chat").
 */
export function resetToWelcome() {
  if (!messagesEl) return;
  const welcome = document.getElementById("welcomeMessage");
  const toRemove = [];
  for (const child of messagesEl.children) {
    if (child !== welcome) toRemove.push(child);
  }
  toRemove.forEach((el) => el.remove());
  scrollToBottom();
}

/**
 * Load a conversation from persisted messages (from PostgreSQL).
 * messages: array of { role, content, payload? } (payload used for assistant bubbles).
 */
export function loadMessages(messages) {
  if (!messagesEl) return;
  const welcome = document.getElementById("welcomeMessage");
  const toRemove = [];
  for (const child of messagesEl.children) {
    if (child !== welcome) toRemove.push(child);
  }
  toRemove.forEach((el) => el.remove());

  if (!Array.isArray(messages) || messages.length === 0) {
    scrollToBottom();
    return;
  }

  for (const m of messages) {
    if (m.role === "user") {
      addUserMessage(m.content);
    } else if (m.role === "assistant") {
      const data = m.payload || { summary: m.content };
      addMessage("bot", buildBotContentHtml(data));
    }
  }
  scrollToBottom();
}
