/**
 * Login page: validates credentials and redirects to chat on success.
 * Session is stored in sessionStorage (cleared when the browser tab closes).
 */

const EXPECTED_EMAIL = "agenticnode@gmail.com";
const EXPECTED_PASSWORD = "agenticnode2026";
const SESSION_KEY = "agentic_node_authenticated";

const form = document.getElementById("loginForm");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const errorEl = document.getElementById("loginError");
const submitBtn = document.getElementById("submitBtn");

form.addEventListener("submit", function (e) {
  e.preventDefault();
  errorEl.hidden = true;
  errorEl.textContent = "";

  const email = (emailInput.value || "").trim().toLowerCase();
  const password = passwordInput.value || "";

  if (!email || !password) {
    errorEl.textContent = "Please enter both email and password.";
    errorEl.hidden = false;
    return;
  }

  if (email !== EXPECTED_EMAIL || password !== EXPECTED_PASSWORD) {
    errorEl.textContent = "Invalid email or password.";
    errorEl.hidden = false;
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Signing in…";
  sessionStorage.setItem(SESSION_KEY, "true");
  window.location.href = "index.html";
});
