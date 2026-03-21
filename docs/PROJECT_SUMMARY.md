<!-- docs/ — primary technical reference for Agentic Node -->
# Agentic Node — Technical and Project Summary

A minute-level technical and functional summary of the Agentic Node application.

---

## 1. Project Overview

**Name:** Agentic Node  
**Purpose:** A production-oriented web application that acts as an **AI Data Analyst** and **HR Knowledge Assistant**. Users ask questions in natural language; the system either runs SQL against a PostgreSQL database (with optional charts) or answers from uploaded documents via RAG. All conversation state is stored server-side; the frontend is a stateless chat UI.

**Core value:**
- **Data questions** → Convert to SQL using only schema (no row data to the LLM), execute, optionally recommend and generate charts (bar, line, pie), return summary + table + chart.
- **Document questions** → Search vector store (ChromaDB) over uploaded PDF/DOCX/TXT, retrieve relevant chunks, generate an answer using an LLM.
- **General/greetings** → Handled with short, bounded responses (greeting reply or polite decline to stay on-topic).

**Deployment model:**
- **Frontend:** Static site (HTML, CSS, JS) deployed on **GitHub Pages**.
- **Backend:** **FastAPI** app deployed on **Railway** (Dockerfile, root directory `backend`).
- **Data:** **PostgreSQL** (Railway or external) for sessions, messages, and analytics schema; **ChromaDB** (persistent on backend filesystem) for RAG; **OpenAI** for LLM and embeddings.

---

## 2. Technology Stack

### 2.1 Backend
| Component | Technology |
|-----------|------------|
| Runtime | Python 3.11 |
| Web framework | FastAPI ≥0.115 |
| ASGI server | Uvicorn (default port 8000 locally; Railway uses PORT, often 8080 or 8000) |
| Config | pydantic-settings, env from `.env` or environment |
| LLM / orchestration | OpenAI API (gpt-4o-mini), LangGraph ≥0.2, LangChain Core |
| Relational DB | PostgreSQL, SQLAlchemy 2.x, psycopg2-binary |
| Vector store | ChromaDB (persistent client, OpenAI text-embedding-3-small) |
| Charts | Matplotlib, pandas, numpy |
| Document parsing | pypdf (PDF), python-docx (DOCX), plain UTF-8 (TXT) |

### 2.2 Frontend
| Component | Technology |
|-----------|------------|
| Delivery | Static HTML/CSS/JS (no build step required; optional npm for tooling) |
| Hosting | GitHub Pages (artifact: `frontend/` directory) |
| API usage | Fetch to backend base URL (injected at deploy time from `BACKEND_URL` secret) |
| Auth (demo) | Session storage flag `agentic_node_authenticated`; demo credentials shown on login page |
| Layout | Responsive (mobile.css) with safe-area support; sidebar overlay on small screens |

### 2.3 Infrastructure and DevOps
| Item | Detail |
|------|--------|
| Repo | GitHub; backend root directory for Railway set to `backend` |
| Backend build | Dockerfile in `backend/` (Python 3.11-slim, system deps for psycopg2/matplotlib) |
| Backend start | `python -m run` (run.py reads PORT, default 8000; Railway can set PORT=8080 or 8000) |
| Frontend deploy | GitHub Actions workflow on push to `main`: replace `window.API_BASE = "__BACKEND_URL__"` with secret, upload `frontend/` as Pages artifact |
| Secrets | Backend: OPENAI_API_KEY, DATABASE_URL, CHROMA_PERSIST_DIR, UPLOAD_DIR (and optional overrides). GitHub: BACKEND_URL for Pages. |

---

## 3. Architecture (High-Level)

- **User/Browser** → HTTPS → **Frontend (GitHub Pages)** → API calls → **Backend (FastAPI on Railway)**.
- **Backend** uses:
  - **PostgreSQL:** Chat sessions, chat messages, and analytics tables (departments, employees, salaries, projects, project_assignments, sales).
  - **ChromaDB:** Persistent vector store for document chunks (collection `documents`, cosine similarity, OpenAI embeddings).
  - **OpenAI:** Chat completions (intent, SQL, chart recommendation, response generation) and embeddings for RAG.

No WebSockets; all interaction is REST (GET/POST). Session affinity is by `session_id` (UUID) and server-side storage.

---

## 4. Backend Application Structure

### 4.1 Entry and Config
- **`backend/run.py`:** Reads `PORT` from environment (default 8000), runs `uvicorn app.main:app --host 0.0.0.0 --port <PORT>`.
- **`backend/app/main.py`:** FastAPI app, lifespan, CORS, route registration. **Lifespan:** Validates DATABASE_URL on Railway (fail if localhost); preloads DB schema; compiles LangGraph pipeline; ensures `chat_sessions` / `chat_messages` tables exist.
- **`backend/app/config.py`:** Pydantic Settings: `openai_api_key`, `model_name` (default gpt-4o-mini), `model_temperature`, `database_url`, `chroma_persist_dir`, `chunk_size`, `chunk_overlap`, `upload_dir`, `max_query_rows`, `sql_timeout_seconds`. Loads from `(.env`, `../.env)`.

### 4.2 API Routes
| Method | Path | Purpose |
|--------|------|--------|
| GET | /health | Liveness; returns `{"status":"healthy","service":"ai-analyst-backend"}`. |
| GET | /api/sessions | List chat sessions (newest first). Sync DB run in thread pool. |
| POST | /api/sessions?title=... | Create session; returns session object. |
| GET | /api/sessions/{id} | Get one session with all messages. |
| DELETE | /api/sessions/{id} | Delete session and messages. |
| POST | /api/query | Main entry: body = question, optional conversation_history, optional session_id. Runs LangGraph pipeline; optionally persists messages; returns QueryResponse (type, summary, table, chart_type, chart_data, chart_image, sql_query, error). Enforces **12 questions per session** (friendly message when exceeded). |
| POST | /api/upload | Multipart file upload (PDF/DOCX/TXT). Saves to UPLOAD_DIR, loads text, chunks, embeds, stores in ChromaDB; returns filename, chunks_stored, message. |

### 4.3 Request/Response Models
- **QueryRequest:** `question` (1–2000 chars), `conversation_history` (list of `{role, content}`, max 20), `session_id` (optional).
- **QueryResponse:** `type`, `chart_type`, `chart_data`, `chart_image` (base64), `table`, `summary`, `sql_query`, `error`.
- **UploadResponse:** `filename`, `chunks_stored`, `message`.

---

## 5. Database (PostgreSQL)

### 5.1 Connection and Schema
- **`app/database/connection.py`:** SQLAlchemy engine and session factory from `DATABASE_URL`.
- **`app/database/schema_loader.py`:** Introspects all tables (columns, types, primary keys, foreign keys), caches in memory. `format_schema_for_llm()` produces a text representation for prompts (schema only, no row data).

### 5.2 Analytics Schema (seed.sql)
Tables: **departments** (id, name, location, budget), **employees** (id, first_name, last_name, email, department_id, job_title, hire_date, status), **salaries** (id, employee_id, amount, effective_date, salary_type), **projects** (id, name, department_id, start_date, end_date, budget, status), **project_assignments** (id, employee_id, project_id, role, assigned_date), **sales** (id, employee_id, product, region, amount, quantity, sale_date). Seed data: 7 departments, 25 employees, salaries, 10 projects, 26 assignments, 40 sales rows.

### 5.3 Chat Schema (app-created)
- **chat_sessions:** id (UUID), title, created_at, updated_at.
- **chat_messages:** id (UUID), session_id (FK to chat_sessions ON DELETE CASCADE), role (user|assistant), content (TEXT), payload (JSONB), created_at. Indexes on session_id and updated_at for listing.

### 5.4 Query Execution
- **`app/database/query_executor.py`:** `validate_sql()` allows only a single SELECT; forbids DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE, GRANT, REVOKE, EXEC, EXECUTE; no semicolon-separated multiple statements. `execute_sql()` runs validated SQL, returns up to `max_query_rows` rows as list of dicts plus column names.

---

## 6. LangGraph Pipeline (Query Flow)

**State (AnalystState):** question, conversation_history, intent, db_schema, sql_query, sql_explanation, query_result, query_columns, chart_type, chart_data, chart_image, x_column, y_column, label_column, text_summary, rag_context, final_response, error.

**Graph:**
1. **START → intent_classifier**  
   Uses OpenAI with system prompt to classify into: `database_query`, `rag_query`, `greeting`, `general_question`. Uses last 6 turns of conversation. Returns JSON `{"intent":"..."}`.

2. **Conditional routing from intent_classifier:**
   - `database_query` → **sql_generator**
   - `rag_query` → **rag_search**
   - Otherwise (greeting, general_question) → **response_generator**

3. **sql_generator:** Receives schema (no row data). Calls OpenAI to generate a single SELECT; writes sql_query (and optional explanation) into state.

4. **execute_query:** Runs validated SQL via query_executor; fills query_result, query_columns (or error).

5. **chart_recommender:** Given question and result preview, calls OpenAI to choose one of: bar, line, pie, table, text; and x_column, y_column, label_column.

6. **Conditional after chart_recommender:** If chart_type in (bar, line, pie) → **chart_generator**, else → **response_generator**.

7. **chart_generator:** Uses matplotlib to produce chart; returns chart_data (Chart.js-style) and chart_image (base64 PNG). On failure, falls back to table.

8. **rag_search:** Calls `search_and_answer(question)`: ChromaDB similarity search (default 5 chunks), formats context string for response_generator (no LLM call here).

9. **response_generator:** Single node that assembles final_response. Branches on intent: for database path uses summary + table/chart; for RAG uses rag_context + LLM to answer; for greeting returns short fixed reply; for general_question returns polite decline. Writes final_response (type, summary, chart_type, chart_data, chart_image, table, sql_query, error).

10. **response_generator → END.**

Session persistence (append_message, update session title) is done in the query route after the graph returns, using session_id when provided.

---

## 7. RAG Pipeline (Upload and Search)

### 7.1 Upload (POST /api/upload)
- Allowed extensions: .pdf, .docx, .txt.
- File saved under `UPLOAD_DIR` as `{uuid12}_{original_filename}`.
- **load_document(file_path):** Dispatches by suffix to pypdf (PDF), python-docx (DOCX), or UTF-8 text (TXT).
- **chunk_text(text, chunk_size, chunk_overlap):** Recursive split on `\n\n`, `\n`, `. `, etc., with overlap (default 1000 chars, 200 overlap).
- **add_documents:** ChromaDB persistent client, collection `documents`, OpenAI embedding function (text-embedding-3-small), metadata includes source filename and chunk index; batches of 100.

### 7.2 Search (RAG query path)
- **search_documents(query, n_results=5):** ChromaDB similarity search (cosine); returns list of {content, metadata}.
- **search_and_answer(question):** Builds a single context string from top chunks with "[Source: ... | Chunk i]" headers; response_generator then uses this plus LLM to produce the answer.

---

## 8. Frontend (Minute Detail)

### 8.1 Pages and Auth
- **login.html:** Form (email, password); demo credentials shown: agenticnode@gmail.com / agenticnode2026. On submit, sets `sessionStorage.agentic_node_authenticated` and redirects to index.html.
- **index.html:** If `agentic_node_authenticated` is not set, redirects to login.html. Contains app shell: sidebar, main chat area, input bar, sidebar overlay. Inline script sets `window.API_BASE` from placeholder `__BACKEND_URL__` (replaced by GitHub Actions with BACKEND_URL secret); fallback to http://localhost:8000 when placeholder is still present.

### 8.2 Chat UI
- **Sidebar:** New chat button, scrollable session list (from GET /api/sessions), per-session delete, Log out link. Session list items show title; active session highlighted. Sidebar is overlay on mobile (toggle via hamburger); tap overlay to close.
- **Main area:** Header (title “Agentic Node”, subtitle), scrollable messages container (welcome message + user/bot bubbles), input bar (Attach File, textarea 2000 chars, Send).
- **Messages:** Bot messages can render: plain text, table (with Download CSV), chart (Chart.js from chart_data + optional chart_image), SQL block, error block. User messages shown as bubbles; payload stored so re-open of session can re-render tables/charts.

### 8.3 API Usage (Frontend)
- **Sessions:** GET /api/sessions on load; POST /api/sessions?title=New%20chat when starting new chat; GET /api/sessions/{id} when switching session; DELETE when deleting a chat.
- **Query:** POST /api/query with question, conversation_history (recent messages), session_id (if any). On success, append user and assistant messages to DOM and optionally persist (backend persists when session_id sent).
- **Upload:** POST /api/upload multipart with file; on success, show message and optionally append to conversation.

### 8.4 Styling and Assets
- **CSS:** base.css (layout, theme variables, header, sidebar toggle), sidebar.css (sidebar, session list), chat.css (messages, bubbles, tables, charts, buttons), input.css (input bar, textarea, buttons), login.css, mobile.css (responsive, safe-area, smaller padding/fonts on small screens).
- **Theme:** Dusty rose (#c9a9a6) and black (#1a1a1a); logo as background image; surfaces and borders from CSS variables.

---

## 9. Security and Limits

- **SQL:** Only SELECT; validation rejects forbidden keywords and multiple statements; no raw row data in SQL-generation prompt.
- **Sessions:** Stored in PostgreSQL; 12 questions per session cap; friendly message when exceeded.
- **Secrets:** API keys and DATABASE_URL from environment; .env not committed; .dockerignore excludes .env in backend image.
- **CORS:** Allow all origins (configurable); credentials allowed.
- **Auth:** Demo-only (sessionStorage); no server-side login validation.

---

## 10. Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| OPENAI_API_KEY | (required) | OpenAI API key. |
| MODEL_NAME | gpt-4o-mini | Chat model for LLM calls. |
| MODEL_TEMPERATURE | 0.0 | LLM temperature. |
| DATABASE_URL | postgresql://... | PostgreSQL connection string. |
| CHROMA_PERSIST_DIR | ./chroma_data | ChromaDB persistence path. |
| UPLOAD_DIR | ./uploads | Directory for uploaded files. |
| CHUNK_SIZE | 1000 | RAG chunk size (characters). |
| CHUNK_OVERLAP | 200 | Overlap between chunks. |
| MAX_QUERY_ROWS | 500 | Max rows returned per SQL query. |
| SQL_TIMEOUT_SECONDS | 30 | Query timeout (seconds); executor uses fetchmany and max_query_rows.) |
| PORT | 8000 (run.py) | Server port (Railway sets PORT). |
| LANGCHAIN_TRACING_V2 | (unset) | Set to `true` to enable LangSmith tracing. |
| LANGCHAIN_API_KEY | (unset) | LangSmith API key (from smith.langchain.com). |
| LANGCHAIN_PROJECT | (unset) | Optional; project name in LangSmith for grouping runs. |

See **docs/LANGSMITH.md** for how to run LangSmith and inspect the LangGraph flow when deployed on Railway and GitHub Pages.

---

## 11. Repo and Deployment Summary

- **GitHub:** Frontend on Pages (branch main, workflow replaces BACKEND_URL in HTML). Backend not built by GitHub; Railway builds from same repo, root directory `backend`, Dockerfile.
- **Railway:** Backend service; Variables: OPENAI_API_KEY, DATABASE_URL (reference to Postgres or literal URL), CHROMA_PERSIST_DIR (e.g. /tmp/chroma_data), UPLOAD_DIR (e.g. /tmp/uploads). Networking: app must listen on the port Railway assigns (often 8000 in UI or 8080 via PORT). Seed DB with backend/seed.sql against Railway Postgres for analytics tables.
- **Diagrams:** `scripts/generate_diagrams.py` (matplotlib) produces `diagrams/architecture_flow.png` and `diagrams/process_flow.png`.

---

## 12. File and Folder Summary

**Backend (Python):**  
main.py, config.py, run.py; api/ (routes_query, routes_upload, routes_sessions); database/ (connection, schema_loader, query_executor, chat_sessions); langgraph/ (graph_builder, nodes: intent_classifier, sql_generator, chart_recommender, response_generator); rag/ (document_loader, embeddings, vector_store, rag_query); charts/ (chart_generator); models/ (request_models, response_models). Plus requirements.txt, seed.sql, Dockerfile, .dockerignore, Procfile, scripts (e.g. seed-railway.ps1).

**Frontend:**  
index.html, login.html; css/ (base, sidebar, chat, input, login, mobile); js/ (api, app, chatUI, inputBar, messageRenderer, utils, config, login); assets/ (agentic_node.png). No server-side code.

**Docs / DevOps:**  
README.md, docs/PROJECT_SUMMARY.md (this file), .github/workflows/deploy-pages.yml, diagrams/ (PNGs).

This document is the single place for a minute-level technical and operational summary of the Agentic Node project.
