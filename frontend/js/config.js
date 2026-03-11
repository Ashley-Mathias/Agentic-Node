/**
 * Frontend config. API_BASE is set in index.html via window.API_BASE.
 */
export function getApiBase() {
  if (typeof window === "undefined") return "";
  return window.API_BASE != null ? window.API_BASE : "";
}
