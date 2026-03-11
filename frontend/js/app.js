/**
 * App entry: wires config, API, chat UI, input bar, and sidebar. No backend changes.
 */
import { getApiBase } from "./config.js";
import * as api from "./api.js";
import * as chatUI from "./chatUI.js";
import { initInputBar } from "./inputBar.js";

const messagesEl = document.getElementById("messages");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const fileInput = document.getElementById("fileInput");

chatUI.initChatUI(messagesEl);

/** Session context: last N user/assistant messages for this chat (cleared on New chat). */
const conversationHistory = [];

document.getElementById("newChatBtn").addEventListener("click", function () {
  conversationHistory.length = 0;
  chatUI.resetToWelcome();
  document.getElementById("appShell").classList.remove("sidebar-open");
});

function sendQuery(question) {
  const apiBase = getApiBase();
  chatUI.addUserMessage(question);
  const loadingEl = chatUI.addLoadingMessage();
  sendBtn.disabled = true;

  conversationHistory.push({ role: "user", content: question });

  api.query(apiBase, question, conversationHistory)
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
