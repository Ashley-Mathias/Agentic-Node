<!-- docs/ folder: project documentation -->
# Running LangSmith and Checking the Flow (Railway + GitHub Pages)

This app uses **LangGraph** for the query pipeline. You can trace every run (intent → SQL/RAG/reply, chart steps, errors) in **LangSmith** so you can debug and inspect the flow in production.

---

## How it works

- **Frontend:** GitHub Pages (static site). Users open the chat UI in the browser.
- **Backend:** Railway. Every question is sent to `POST /api/query` on your Railway URL. The backend runs the LangGraph pipeline.
- **LangSmith:** When tracing is enabled, the LangGraph/LCEL calls on Railway automatically send traces to LangSmith. You do **not** need to change any application code; you only set environment variables on Railway.

So: **User asks a question on GitHub Pages → request hits Railway → LangGraph runs → trace is sent to LangSmith.** You then open the LangSmith dashboard to see the flow.

---

## 1. Get a LangSmith API key

1. Go to [https://smith.langchain.com](https://smith.langchain.com) and sign up or log in.
2. Click your profile (bottom-left) → **Settings** → **API Keys**.
3. Create an API key and copy it (starts with `lsv2_pt_...`). You will use it only on the backend (Railway), never in the frontend.

---

## 2. Enable tracing on Railway

1. Open the [Railway dashboard](https://railway.app/dashboard) and select your **backend** project/service (the one that runs the FastAPI app).
2. Go to the **Variables** tab for that service.
3. Add these variables:

   | Variable | Value | Required |
   |----------|--------|----------|
   | `LANGCHAIN_TRACING_V2` | `true` | Yes |
   | `LANGCHAIN_API_KEY` | Your LangSmith API key (e.g. `lsv2_pt_...`) | Yes |
   | `LANGCHAIN_PROJECT` | e.g. `agentic-node` or `agentic-node-production` | No (optional; groups runs in LangSmith) |

4. Save. Railway will redeploy the service with the new variables. No code changes are required.

---

## 3. Trigger a run and see the flow

1. Open your **frontend** (GitHub Pages URL, e.g. `https://<your-username>.github.io/agentic-node/` or your custom domain).
2. Log in (if your app has demo auth) and start a **new chat**.
3. Ask a question that hits the pipeline, for example:
   - **Database:** “Show total sales by region” or “How many employees are in each department?”
   - **RAG:** A question about an uploaded document (e.g. Global Travel Policy).
   - **General:** “Hello” (you’ll see intent_classifier → response_generator).
4. In [LangSmith](https://smith.langchain.com), open **Projects** (or **Traces**) and select the project you set in `LANGCHAIN_PROJECT` (or the default project).
5. You should see a new **run** for that request. Click it to see:
   - The full **graph flow** (intent_classifier → sql_generator / rag_search / response_generator, etc.).
   - **Inputs/outputs** for each node.
   - **Latency** per step.
   - **Errors** if something failed.
   - **LLM calls** (prompts and responses) when applicable.

That’s the “flow” of your pipeline; you can inspect it for every query that hits Railway.

---

## 4. Optional: run and trace locally

To test LangSmith with the same backend code locally (without deploying):

1. In `backend/`, copy `.env.example` to `.env` if you haven’t already.
2. In `.env`, set:
   - `LANGCHAIN_TRACING_V2=true`
   - `LANGCHAIN_API_KEY=<your-langsmith-api-key>`
   - `LANGCHAIN_PROJECT=agentic-node-local` (optional)
3. Run the backend, e.g. `python -m run` or `uvicorn app.main:app --reload`.
4. Point the frontend at localhost (e.g. set `window.API_BASE` to `http://localhost:8000` in the frontend or use a local frontend that already does).
5. Send a query; the run will appear in LangSmith under the project you set.

---

## 5. Summary

| Goal | Action |
|------|--------|
| **Trace production (Railway + GitHub Pages)** | Add `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, and optionally `LANGCHAIN_PROJECT` to the **Railway** service Variables. Use the GitHub Pages app as usual; each query is traced. |
| **See the flow** | Open [smith.langchain.com](https://smith.langchain.com) → your project → click a run → inspect the graph, nodes, and LLM calls. |
| **Trace locally** | Set the same three env vars in `backend/.env` and run the backend; use the frontend against localhost. |

No frontend or GitHub Pages configuration is needed for LangSmith; tracing is entirely on the backend (Railway or local).
