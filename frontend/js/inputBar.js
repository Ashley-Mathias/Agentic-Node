/**
 * Input bar: send on button/Enter, attach file, textarea auto-resize.
 */
export function initInputBar(options) {
  const { messageInput, sendBtn, fileInput, onSend, onUpload } = options;
  if (!messageInput || !sendBtn) return;

  function submit() {
    const text = messageInput.value.trim();
    if (!text) return;
    onSend(text);
    messageInput.value = "";
    messageInput.style.height = "auto";
  }

  sendBtn.addEventListener("click", submit);

  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  });

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      const file = fileInput.files[0];
      if (file) onUpload(file);
    });
  }

  messageInput.addEventListener("input", () => {
    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
  });

  messageInput.focus();
}
