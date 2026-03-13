/**
 * Vercel serverless function: returns a script that sets window.API_BASE.
 * Set env var API_BASE (or BACKEND_URL) in Vercel project settings to your FastAPI backend URL.
 */
module.exports = (req, res) => {
  const apiBase = process.env.API_BASE || process.env.BACKEND_URL || "http://localhost:8000";
  res.setHeader("Content-Type", "application/javascript");
  res.setHeader("Cache-Control", "public, max-age=60");
  res.end("window.API_BASE = " + JSON.stringify(apiBase) + ";\n");
};
