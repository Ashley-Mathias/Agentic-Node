# Agentic-Node

A production-ready backend that combines an **AI Data Analyst** and **HR Knowledge Assistant**. It converts natural language questions into SQL, runs queries against PostgreSQL, returns results as text, tables, and charts, and answers document-based questions via a RAG pipeline. The API is REST-only; a separate chat frontend is provided in the `frontend/` folder.

---

## Screenshots

| Chat interface | Response with table |
|----------------|---------------------|
| ![Chat interface](screenshots/01-chat-interface.png) | ![Response with table](screenshots/02-response-table.png) |
| *Welcome message, user query, and input bar.* | *Summary plus data table with Download CSV.* |

| Response with chart | Attach file dialog |
|---------------------|--------------------|
| ![Response with chart](screenshots/03-response-chart.png) | ![Attach file dialog](screenshots/04-attach-file-dialog.png) |
| *Bar chart with Download PNG.* | *File picker when using "Attach" for RAG documents.* |

| Sidebar / menu |
|----------------|
| ![Sidebar](screenshots/05-sidebar-login.png) |
| *Sidebar with New chat and Log out; login screen.* |

---

## Table of Contents

- [Screenshots](#screenshots)
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Workflows](#workflows)
- [Security](#security)
- [License](#license)

---

## Features

- **Natural language to SQL**: User questions are classified and turned into PostgreSQL `SELECT` queries using only the database schema (table and column names, relationships). Raw row data is never sent to the LLM for query generation.
- **Structured responses**: Results are returned in three forms when applicable: a short text summary, a tabular payload, and chart data (with optional base64 PNG) for bar, line, or pie visualizations.
- **RAG over documents**: Upload PDF, DOCX, or TXT files; they are chunked, embedded with OpenAI, and stored in ChromaDB. Questions about policy or HR content are answered from retrieved chunks.
- **Intent routing**: A LangGraph pipeline classifies each question as `database_query`, `rag_query`, or `general_question` and routes to the appropriate branch (SQL execution + charting vs. document search vs. general assistant).
- **Chart recommendation and generation**: For database results, the system suggests a chart type (bar, line, pie, table, or text) and can generate matplotlib charts returned as JSON and base64 images.

---

## Architecture Overview

- **API layer**: FastAPI with REST endpoints; no WebSockets or frontend.
- **Orchestration**: LangGraph state machine with nodes for intent classification, SQL generation, query execution, chart recommendation, chart generation, RAG search, and response assembly.
- **Data**: PostgreSQL for relational data; SQLAlchemy for connection and schema introspection; a dedicated query executor that validates and runs only safe `SELECT` statements.
- **RAG**: Document loader (PDF/DOCX/TXT), chunking, OpenAI embeddings, ChromaDB for vector storage and similarity search.
- **Charts**: Matplotlib (and pandas) to produce bar, line, and pie charts; output as JSON and base64-encoded PNG.

---

## Project Structure

```
backend/
  app/
    main.py                 # FastAPI app, lifespan, route registration
    config.py               # Settings (pydantic-settings), OpenAI client
    api/
      routes_query.py       # POST /api/query
      routes_upload.py      # POST /api/upload
    database/
      connection.py         # SQLAlchemy engine and session factory
      schema_loader.py       # Introspect and cache DB schema for LLM
      query_executor.py      # Validate and execute read-only SQL
    langgraph/
      graph_builder.py      # LangGraph pipeline definition and routing
      nodes/
        intent_classifier.py # database_query | rag_query | general_question
        sql_generator.py    # NL -> SQL (schema-only context)
        chart_recommender.py# bar | line | pie | table | text
        response_generator.py # Final JSON response assembly
    rag/
      document_loader.py    # Load and chunk PDF/DOCX/TXT
      embeddings.py         # OpenAI embeddings
      vector_store.py      # ChromaDB add and search
      rag_query.py         # Search and build context for LLM
    charts/
      chart_generator.py   # Matplotlib charts -> JSON + base64 PNG
    models/
      request_models.py    # Pydantic request bodies
      response_models.py   # Pydantic response models
  requirements.txt
  .env.example
  seed.sql                 # DB schema and sample data for agentic_node
.env.example               # Root-level env template (optional)
.gitignore
```

---

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ (e.g. database `agentic_node` on port 5433)
- OpenAI API key (for LLM and embeddings)

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/AshleyMathias/Agentic-Node.git
   cd Agentic-Node
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate

   pip install -r backend/requirements.txt
   ```

---

## Configuration

Copy the example environment file and set your values:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` (or `.env` in the project root if you run from there). Required and optional variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `MODEL_NAME` | Chat model for LLM | `gpt-4o-mini` |
| `MODEL_TEMPERATURE` | LLM temperature | `0.0` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5433/agentic_node` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./chroma_data` |
| `UPLOAD_DIR` | Directory for uploaded files | `./uploads` |
| `CHUNK_SIZE` | RAG chunk size (chars) | `1000` |
| `CHUNK_OVERLAP` | RAG chunk overlap (chars) | `200` |
| `MAX_QUERY_ROWS` | Max rows returned per SQL query | `500` |
| `SQL_TIMEOUT_SECONDS` | Query timeout (seconds) | `30` |

---

## Database Setup

1. Create the database (if not already created):

   ```bash
   psql -U postgres -p 5433 -c "CREATE DATABASE agentic_node;"
   ```

2. Run the seed script to create tables and load sample data:

   ```bash
   psql -U postgres -p 5433 -d agentic_node -f backend/seed.sql
   ```

   This creates tables such as `departments`, `employees`, `salaries`, `projects`, `project_assignments`, and `sales`, and populates them with sample HR and analytics data.

---

## Running the Application

From the project root:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or from the repo root with the module path:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

---

## API Reference

### Health Check

- **GET** `/health`  
  Returns service status. No body.

### Query (Data Analyst and RAG)

- **POST** `/api/query`  
  Accepts a natural language question and returns a structured response (summary, optional table, optional chart data/image).

  **Request body:**

  ```json
  {
    "question": "Show employee salary distribution by department"
  }
  ```

  **Response fields (example):**

  | Field | Type | Description |
  |-------|------|-------------|
  | `type` | string | One of `chart`, `table`, `text`, `rag`, `error` |
  | `chart_type` | string or null | `bar`, `line`, `pie`, etc., when applicable |
  | `chart_data` | object or null | Chart.js-style labels/datasets |
  | `chart_image` | string or null | Base64-encoded PNG |
  | `table` | array of objects or null | Query result rows |
  | `summary` | string | Natural language summary or answer |
  | `sql_query` | string or null | Generated SQL (for database queries) |
  | `error` | string or null | Error message if something failed |

### Chat Sessions (PostgreSQL; no browser memory)

All chat sessions and messages are stored in PostgreSQL. The frontend does not use browser/local storage for conversation memory.

- **GET** `/api/sessions`  
  List all chat sessions (for the sidebar), ordered by `updated_at` descending. Returns `{ "sessions": [ { "id", "title", "created_at", "updated_at" }, ... ] }`.

- **POST** `/api/sessions?title=New+chat`  
  Create a new session. Returns the new session object.

- **GET** `/api/sessions/{session_id}`  
  Get one session with all messages (for loading a conversation). Returns `{ "id", "title", "created_at", "updated_at", "messages": [ { "id", "role", "content", "payload", "created_at" }, ... ] }`.

- **DELETE** `/api/sessions/{session_id}`  
  Delete a session and all its messages from the database. When the user deletes a chat in the frontend, this is called so the deletion is synchronous with the DB.

The **POST** `/api/query` body may include an optional `session_id`. When present, the backend appends the user message and assistant response (with full payload for re-rendering) to that session and updates its title from the user message.

### Upload Documents (RAG)

- **POST** `/api/upload`  
  Upload a single file to the RAG knowledge base. Supported types: PDF, DOCX, TXT.

  **Request:** `multipart/form-data` with a file field named `file`.

  **Response:**

  | Field | Type | Description |
  |-------|------|-------------|
  | `filename` | string | Original filename |
  | `chunks_stored` | integer | Number of chunks stored in the vector store |
  | `message` | string | Success message |

---

## Workflows

### Data Analyst Workflow

1. User sends a question (e.g. "Show monthly sales trend") to `POST /api/query`.
2. **Intent classifier** labels it as `database_query`.
3. **SQL generator** produces a `SELECT` using only the loaded database schema.
4. **Query executor** validates (read-only) and runs the SQL on PostgreSQL; results are not sent back to the LLM for SQL generation.
5. **Chart recommender** chooses bar, line, pie, table, or text from the result shape and question.
6. **Chart generator** (if applicable) builds a matplotlib chart and returns JSON + base64 PNG.
7. **Response generator** formats summary, table, and chart into the final JSON response.

### RAG Document Workflow

**Ingestion (upload):**

1. User uploads a file via `POST /api/upload`.
2. Document is loaded (PDF/DOCX/TXT), chunked, and embedded with OpenAI.
3. Chunks are stored in ChromaDB with metadata (e.g. source filename).

**Query:**

1. User asks a question (e.g. "What is the vacation policy?") via `POST /api/query`.
2. **Intent classifier** labels it as `rag_query`.
3. **RAG search** retrieves relevant chunks from ChromaDB.
4. **Response generator** uses the retrieved context to produce an answer (no database or chart).

---

## Security

- **No raw database data to the LLM for SQL**: The SQL generator receives only schema information (tables, columns, types, primary/foreign keys). Row data is never used for generating or refining SQL. The backend executes the generated query and returns results to the client; only a limited result preview may be used for writing the natural language summary.
- **Read-only SQL**: The query executor allows only `SELECT` statements. Commands such as `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, and similar are rejected. Multiple statements and dangerous patterns are blocked.
- **Secrets**: Do not commit `.env`. Use `.env.example` as a template and keep API keys and database credentials out of version control.

---

## License

See [LICENSE](LICENSE) in this repository.
