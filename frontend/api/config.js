/**
 * Vercel serverless function: returns a script that sets window.API_BASE.
 * Set env var API_BASE (or BACKEND_URL) in Vercel project settings to your FastAPI backend URL.
 */
export function GET() {
  const apiBase = process.env.API_BASE || process.env.BACKEND_URL || "http://localhost:8000";
  return new Response("window.API_BASE = " + JSON.stringify(apiBase) + ";\n", {
    headers: {
      "Content-Type": "application/javascript",
      "Cache-Control": "public, max-age=60",
    },
  });
}
