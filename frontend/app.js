(function () {
  "use strict";

  // Use window.API_BASE from index.html, or empty string for same-origin (e.g. when served by backend)
  var API_BASE = (typeof window !== "undefined" && window.API_BASE !== undefined) ? window.API_BASE : "";

  var messagesEl = document.getElementById("messages");
  var messageInput = document.getElementById("messageInput");
  var sendBtn = document.getElementById("sendBtn");
  var fileInput = document.getElementById("fileInput");

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addMessage(role, contentHtml) {
    var wrap = document.createElement("div");
    wrap.className = "message message-" + role;
    wrap.innerHTML = "<div class=\"bubble\">" + contentHtml + "</div>";
    messagesEl.appendChild(wrap);
    scrollToBottom();
    return wrap;
  }

  function addUserMessage(text) {
    addMessage("user", "<p>" + escapeHtml(text) + "</p>");
  }

  function addLoadingMessage() {
    var wrap = document.createElement("div");
    wrap.className = "message message-bot message-loading";
    wrap.innerHTML = "<div class=\"bubble\">Thinking</div>";
    messagesEl.appendChild(wrap);
    scrollToBottom();
    return wrap;
  }

  function buildBotContent(data) {
    var html = "";

    if (data.error) {
      html += "<div class=\"bubble-error\">" + escapeHtml(data.error) + "</div>";
    }

    if (data.summary) {
      html += "<p>" + escapeHtml(data.summary).replace(/\n/g, "<br>") + "</p>";
    }

    if (data.table && Array.isArray(data.table) && data.table.length > 0) {
      var keys = Object.keys(data.table[0]);
      var thead = "<tr>";
      keys.forEach(function (k) {
        thead += "<th>" + escapeHtml(k) + "</th>";
      });
      thead += "</tr>";
      var tbody = "";
      data.table.forEach(function (row) {
        tbody += "<tr>";
        keys.forEach(function (k) {
          var val = row[k];
          tbody += "<td>" + escapeHtml(val != null ? String(val) : "") + "</td>";
        });
        tbody += "</tr>";
      });
      html += "<div class=\"bubble-table-wrap\"><table><thead>" + thead + "</thead><tbody>" + tbody + "</tbody></table></div>";
    }

    if (data.chart_image) {
      html += "<div class=\"bubble-chart\"><img src=\"data:image/png;base64," + escapeHtml(data.chart_image) + "\" alt=\"Chart\" /></div>";
    }

    if (data.sql_query) {
      html += "<div class=\"bubble-sql\"><span class=\"bubble-sql-label\">Generated SQL</span>" + escapeHtml(data.sql_query) + "</div>";
    }

    return html || "<p>No response content.</p>";
  }

  function replaceLoadingWithResponse(loadingEl, data) {
    var content = buildBotContent(data);
    loadingEl.classList.remove("message-loading");
    loadingEl.querySelector(".bubble").innerHTML = content;
    scrollToBottom();
  }

  function sendQuery(question) {
    if (!question.trim()) return;

    addUserMessage(question);
    messageInput.value = "";
    messageInput.style.height = "auto";
    var loadingEl = addLoadingMessage();
    sendBtn.disabled = true;

    fetch(API_BASE + "/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error("Request failed: " + res.status);
        return res.json();
      })
      .then(function (data) {
        replaceLoadingWithResponse(loadingEl, data);
      })
      .catch(function (err) {
        replaceLoadingWithResponse(loadingEl, { error: err.message, summary: "" });
      })
      .finally(function () {
        sendBtn.disabled = false;
      });
  }

  function handleUpload(file) {
    if (!file) return;

    addUserMessage("Uploaded: " + file.name);
    var loadingEl = addLoadingMessage();
    sendBtn.disabled = true;

    var formData = new FormData();
    formData.append("file", file);

    fetch(API_BASE + "/api/upload", {
      method: "POST",
      body: formData,
    })
      .then(function (res) {
        if (!res.ok) return res.json().then(function (d) { throw new Error(d.detail || res.status); });
        return res.json();
      })
      .then(function (data) {
        var msg = data.message || "Uploaded " + data.chunks_stored + " chunks from " + data.filename + ".";
        replaceLoadingWithResponse(loadingEl, { summary: msg });
      })
      .catch(function (err) {
        replaceLoadingWithResponse(loadingEl, { error: err.message, summary: "" });
      })
      .finally(function () {
        sendBtn.disabled = false;
        fileInput.value = "";
      });
  }

  sendBtn.addEventListener("click", function () {
    sendQuery(messageInput.value.trim());
  });

  messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuery(messageInput.value.trim());
    }
  });

  fileInput.addEventListener("change", function () {
    var file = fileInput.files[0];
    handleUpload(file);
  });

  messageInput.addEventListener("input", function () {
    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
  });

  messageInput.focus();
})();
