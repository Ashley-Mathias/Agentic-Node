/**
 * Frontend config. API_BASE is set in index.html via window.API_BASE
 * (GitHub Actions replaces __BACKEND_URL__ with your Railway HTTPS URL).
 */
export function getApiBase() {
  if (typeof window === "undefined") return "";
  const base = window.API_BASE != null ? String(window.API_BASE).replace(/\/$/, "") : "";
  // Warn when deployed on GitHub Pages but API still points at localhost (sessions will fail).
  try {
    const host = window.location.hostname || "";
    if (host.endsWith("github.io") && (base.includes("localhost") || base.includes("127.0.0.1"))) {
      console.warn(
        "[Agentic Node] API_BASE points to localhost on GitHub Pages. Set repo secret BACKEND_URL and redeploy, or set window.API_BASE to your Railway URL."
      );
    }
  } catch (_) {}
  return base;
}
