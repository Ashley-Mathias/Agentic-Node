<!-- frontend/ folder: static UI; see css/, js/, assets/ -->
# Frontend – AI Data Analyst & HR Knowledge Assistant

Static chatbot UI that talks to the backend REST API. No build step; plain HTML, CSS, and JavaScript. Modular layout for easier maintenance.

---

## Structure

| Path | Role |
|------|------|
| `index.html` | Shell, `window.API_BASE`, and script/style links |
| `css/base.css` | Reset, layout, header |
| `css/chat.css` | Messages, bubbles, table/chart/sql/error in bubbles |
| `css/input.css` | Input bar, textarea, buttons |
| `js/config.js` | `getApiBase()` from `window.API_BASE` |
| `js/utils.js` | `escapeHtml()` |
| `js/api.js` | `query(apiBase, question)`, `upload(apiBase, file)` |
| `js/messageRenderer.js` | `buildBotContentHtml(data)` for bot bubbles |
| `js/chatUI.js` | `initChatUI(container)`, `addUserMessage`, `addLoadingMessage`, `replaceLoadingWithResponse` |
| `js/inputBar.js` | `initInputBar({ messageInput, sendBtn, fileInput, onSend, onUpload })` |
| `js/app.js` | Entry: wires config, api, chatUI, inputBar (no backend changes) |

---

## How the frontend connects to the backend

1. **API base URL**  
   The frontend sends all requests to a single base URL (the backend). This is set in `index.html`:

   ```html
   <script>
     window.API_BASE = "http://localhost:8000";
   </script>
   ```

   Change `http://localhost:8000` if your backend runs on another host or port (e.g. `http://192.168.1.10:8000` or `https://api.example.com`).

2. **Endpoints used**  
   `js/api.js` is used by `js/app.js` to call two backend endpoints:

   | Action        | Method | URL                | Body / usage                          |
   |---------------|--------|--------------------|----------------------------------------|
   | Ask question  | POST   | `{API_BASE}/api/query`  | JSON: `{ "question": "..." }`          |
   | Upload file   | POST   | `{API_BASE}/api/upload` | `multipart/form-data` with field `file` |

   So with `API_BASE = "http://localhost:8000"`, the frontend calls:
   - `http://localhost:8000/api/query`
   - `http://localhost:8000/api/upload`

3. **CORS**  
   When the frontend is served from a different origin than the backend (e.g. frontend on port 5500, backend on 8000), the browser enforces CORS. The backend already sends `Access-Control-Allow-Origin: *`, so the browser allows these cross-origin requests.

4. **Same origin vs separate**  
   - **Same origin**: If you serve the frontend from the backend (e.g. backend mounts the `backend/static` folder at `/`), you can set `window.API_BASE = ""` so requests go to the same host (e.g. `/api/query`).
   - **Separate (this folder)**: Serve this `frontend/` folder from any HTTP server (different port). Set `window.API_BASE = "http://localhost:8000"` (or your backend URL). The backend must be running and CORS is already enabled.

---

## Run the frontend (separate from backend)

1. **Start the backend** (from the project root):

   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be at `http://localhost:8000`.

2. **Serve the frontend** from this folder. Pick one:

   **Option A – Python:**

   ```bash
   cd frontend
   python -m http.server 5500
   ```

   **Option B – Node (npx):**

   ```bash
   cd frontend
   npx serve -l 5500
   ```

   Then open: **http://localhost:5500**

3. **Point the frontend at the backend**  
   In `frontend/index.html`, ensure:

   ```html
   window.API_BASE = "http://localhost:8000";
   ```

   Now “Send” and “Attach” in the chatbot use `http://localhost:8000/api/query` and `http://localhost:8000/api/upload`.

---

## Summary

| Step | What to do |
|------|-------------|
| 1 | Start backend: `cd backend && uvicorn app.main:app --reload --port 8000` |
| 2 | Set `window.API_BASE` in `frontend/index.html` to your backend URL (e.g. `http://localhost:8000`) |
| 3 | Serve `frontend/` (e.g. `python -m http.server 5500` in `frontend`) |
| 4 | Open the frontend URL in the browser (e.g. `http://localhost:5500`) |

The connection is: **browser (frontend)** → HTTP requests to **API_BASE** → **backend (FastAPI)**.
