# Deploy Agentic Node (GitHub Pages + Railway)

## What’s set up

- **Frontend** → GitHub Pages (via GitHub Actions)
- **Backend** → Railway (Python + PostgreSQL)

---

## Step 1: Deploy backend to Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. **New Project** → **Deploy from GitHub repo** → select `Agentic-Node`.
3. Add two services:
   - **PostgreSQL** (database)
   - **Empty Service** (backend)
4. Configure the **Empty Service**:
   - **Settings** → **Root Directory**: `backend`
   - **Variables**:
     - `OPENAI_API_KEY` = your OpenAI API key
     - `DATABASE_URL` = copy from the PostgreSQL service variables
     - `CHROMA_PERSIST_DIR` = `/tmp/chroma_data` (optional)
     - `UPLOAD_DIR` = `/tmp/uploads` (optional)
5. **Settings** → **Networking** → **Generate Domain**.
6. Copy the public URL (e.g. `https://xxx.up.railway.app`).

---

## Step 2: Enable GitHub Pages and add backend URL

1. In your repo on GitHub: **Settings** → **Pages**.
2. Under **Source**, choose **GitHub Actions**.
3. **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:
   - **Name**: `BACKEND_URL`
   - **Value**: your Railway URL (e.g. `https://xxx.up.railway.app`, no trailing slash).

---

## Step 3: Deploy frontend

1. Push to `main` (or re-run the workflow):
   - **Actions** → **Deploy to GitHub Pages** → **Run workflow**.
2. After it finishes, your site is at:
   - `https://<your-username>.github.io/Agentic-Node/`

---

## Summary

| Component | URL |
|-----------|-----|
| Frontend (GitHub Pages) | `https://<username>.github.io/Agentic-Node/` |
| Backend (Railway) | `https://<your-app>.up.railway.app` |

Both GitHub Pages and Railway have free tiers.
