# Deploying Agentic Node

## Architecture

- **Frontend**: Static HTML/JS/CSS + Vercel serverless `/api/config` (sets backend URL). Deploy to **Vercel**.
- **Backend**: FastAPI (Python) with PostgreSQL, Chroma, LangGraph. Deploy to **Railway**, **Render**, **Fly.io**, or any host that runs Python and has PostgreSQL.

The frontend calls the backend using `window.API_BASE`. On Vercel, that value is set by the `/api/config` serverless function from the `API_BASE` environment variable.

---

## 1. Deploy frontend to Vercel

1. Push the repo to GitHub (if not already).
2. In [Vercel](https://vercel.com), **Import** the project.
3. Set **Root Directory** to `frontend` (so static files and `api/` are at the project root for Vercel).
4. Leave **Build Command** empty (static site).
5. **Environment variables** (Project Settings → Environment Variables):
   - `API_BASE` = your backend URL, e.g. `https://your-backend.up.railway.app` (no trailing slash).
6. Deploy. The site will be at `https://your-project.vercel.app`.

The `/api/config` serverless function will return `window.API_BASE = "https://...";` so the frontend talks to your backend.

---

## 2. Deploy backend (FastAPI)

The backend needs:

- **Python 3.10+**
- **PostgreSQL** (for chat sessions and analytics DB)
- **Environment variables**: `OPENAI_API_KEY`, `DATABASE_URL`, optionally `CHROMA_PERSIST_DIR`, `UPLOAD_DIR`

### Option A: Railway

1. Create a new project, add **PostgreSQL** and a **Web Service**.
2. Connect the repo; set **Root Directory** to `backend` (or where your FastAPI app lives).
3. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set env vars: `OPENAI_API_KEY`, `DATABASE_URL` (from Railway Postgres), etc.
5. Deploy. Copy the public URL and set it as `API_BASE` in Vercel.

### Option B: Render

1. New **Web Service**; connect repo; set root to `backend`.
2. Build: `pip install -r requirements.txt` (or your install command).
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add **PostgreSQL** and set `DATABASE_URL`. Set `OPENAI_API_KEY` and others.
5. Use the Render URL as `API_BASE` in Vercel.

### CORS

The backend already allows all origins (`allow_origins=["*"]`). For production you can restrict to your Vercel domain in `backend/app/main.py` if you prefer.

---

## 3. After deployment

1. **Frontend**: Open `https://your-project.vercel.app`. Log in (client-side only; no real auth).
2. **Backend**: Ensure PostgreSQL has run migrations (e.g. `backend/migrations/001_chat_sessions.sql`) so `chat_sessions` and `chat_messages` exist.
3. Set **API_BASE** in Vercel to your live backend URL so the chat and sessions work.

---

## Local development

- **Frontend**: From repo root, `cd frontend && python -m http.server 5500` (or use the project’s `start-frontend.ps1`). No `/api/config` locally; `index.html` falls back to `window.API_BASE = "http://localhost:8000"`.
- **Backend**: Run FastAPI on port 8000 (e.g. `uvicorn app.main:app --reload` from `backend/`). Use a local PostgreSQL and `.env` with `OPENAI_API_KEY`, `DATABASE_URL`, etc.
