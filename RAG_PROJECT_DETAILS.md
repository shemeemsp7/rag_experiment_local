
# RAG Project: Implementation Details

## 1. Project Overview
A local Retrieval-Augmented Generation (RAG) pipeline that enables an LLM to answer questions using private local documents (PDF, TXT) without data leaving the machine. Documents are organised into named **collections** and optional **topics** in Qdrant, and chat retrieval can be scoped to a specific collection.

## 2. Tech Stack (as implemented)

| Layer | Technology |
|---|---|
| **LLM Inference** | Ollama — `llama3.1:8b` (128K context) |
| **Embedding Model** | `nomic-embed-text` via Ollama (768-dim vectors, COSINE distance) |
| **Vector Database** | Qdrant (local, port 6333) |
| **Orchestration** | LangChain (`CharacterTextSplitter`, chunk 1000 / overlap 100) |
| **Backend** | FastAPI + Uvicorn (port 8000) |
| **Frontend** | React 18 + Vite (port 3000, proxied to 8000) |
| **Python** | 3.11, virtual environment `venv311` |

## 3. Implementation Phases

### ✅ Phase 1 — Environment Setup
- Ollama installed and running; `llama3.1:8b` and `nomic-embed-text` pulled.
- Python 3.11 venv created (`venv311`), `requirements.txt` installed.
- Qdrant running locally on port 6333.

### ✅ Phase 2 — Backend API (FastAPI)
Key endpoints in `backend/app.py`:

| Method | Endpoint | Notes |
|--------|----------|-------|
| `POST` | `/upload` | Saves file to `data/` |
| `GET` | `/documents` | Lists filenames on disk |
| `GET` | `/documents/info` | Returns `[{filename, collection, topic}]` scraped from Qdrant payloads |
| `POST` | `/ingest` | Chunks, embeds, upserts to named collection; creates collection if needed |
| `POST` | `/chat` | RAG: embed query → Qdrant search → Ollama LLM; accepts `collection_name`/`topic` filter |
| `DELETE` | `/documents/{filename}` | Removes file's vectors; drops collection if it becomes empty |
| `GET` | `/collections` | Lists all Qdrant collections |
| `GET` | `/collection/{name}` | Returns collection info |
| `POST` | `/search` | Vector search with optional metadata filters |
| `GET` | `/llm-models` | Lists models available in Ollama |

### ✅ Phase 3 — Frontend Web UI (React + Vite)

| Component | Responsibility |
|-----------|---------------|
| `App.jsx` | Root layout, global state (`docsMetadata`, selections), LLM model picker |
| `DocumentUpload.jsx` | Upload + ingest in one step; select existing collection or create new one; enter optional topic |
| `DocumentList.jsx` | Sidebar list of documents grouped/sorted by **Collection**, **Topic**, or **Name** (collapsible groups, badges, delete) |
| `ChatInterface.jsx` | Chat panel with message history; collection/topic dropdown to scope RAG retrieval |
| `api.js` | All fetch calls to the backend |

### ✅ Phase 4 — Retrieval & Generation (RAG)
Implemented in `backend/chat_service.py`:
1. Embed user question with `nomic-embed-text` (768-dim).
2. Search the target Qdrant collection (or all collections if none selected) for top-k similar chunks.
3. Build a strict "use only the provided context" prompt.
4. Stream response from Ollama (`llama3.1:8b`).

### ✅ Phase 5 — Integration & Testing
- End-to-end flow: upload → ingest → chat verified.
- Unit tests in `backend/tests/` covering `chat_service`, `ingest_service`, `file_service`.
- Logging at every API boundary.

### ✅ Phase 6 — Enhancements
- LLM model selector in header (persisted to `localStorage`).
- Collection/topic metadata stored in each chunk's Qdrant payload.
- `GET /documents/info` endpoint aggregates per-file collection+topic from Qdrant without a separate metadata store.

### ✅ Phase 7 — Per-Collection/Topic Organisation
Implemented in response to the enhancement plan in `RAG_COLLECTION_IMPLEMENTATION.md`:

**Backend changes:**
- `ingest_service.py` — accepts `collection_name` and `topic`; creates the Qdrant collection if it doesn't exist. Point IDs are deterministic UUIDs keyed on `(collection:filename:chunk_index)` so:
  - Re-ingesting the same file replaces exactly its own chunks (idempotent).
  - Multiple files in the same collection never overwrite each other.
- `app.py` `DELETE /documents/{filename}` — filters by `payload.filename` (not the chunk text), accepts `?collection_name=` to target only the correct collection, and deletes the collection itself when its last file is removed.
- `app.py` `POST /chat` — accepts `collection_name` and `topic` to scope vector search.

**Frontend changes:**
- `DocumentUpload.jsx` — collection dropdown (existing collections) + free-text new-collection input + topic field.
- `DocumentList.jsx` — three-mode view: **Group by Collection** (default), **Group by Topic**, **Sort by Name**; collapsible group headers show file count and colour-coded badge.
- `ChatInterface.jsx` — collection/topic filter dropdown; selected filter is passed to every `/chat` request.
- `api.js` — `listCollections()`, `listDocumentsWithMetadata()`, `deleteDocument(filename, collectionName)` updated accordingly.

## 4. Directory Structure (current)
```
RAG_EXPERIMENT/
├── ingest.py                 # Standalone ingest script (also exports client, models, helpers)
├── chat.py                   # Standalone CLI chat script
├── requirements.txt
├── backend/
│   ├── app.py                # All FastAPI endpoints
│   ├── chat_service.py       # RAG logic (embed → search → LLM)
│   ├── ingest_service.py     # Chunk, embed, upsert; deterministic UUIDs
│   ├── file_service.py       # save_file, list_files
│   └── tests/
├── frontend/
│   ├── vite.config.js        # port 3000, proxy /api → localhost:8000
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       ├── index.css
│       └── components/
│           ├── DocumentUpload.jsx
│           ├── DocumentList.jsx
│           └── ChatInterface.jsx
└── data/                     # Uploaded files (git-ignored)
```

## 5. Key Design Decisions

- **Deterministic chunk IDs** — `uuid5(NAMESPACE_DNS, "{collection}:{filename}:{i}")` ensures idempotent re-ingest and prevents cross-file ID collisions within the same collection.
- **No separate metadata DB** — collection/topic information lives entirely in Qdrant point payloads; `/documents/info` scrolls all collections to reconstruct the list.
- **Lazy collection creation** — collections are created at ingest time if they don't exist; deleted automatically at delete time when empty.
- **Scoped RAG** — when a collection is selected in the chat, only that collection's vectors are searched, improving relevance and speed.

## 6. Running the Project
```bash
# Backend (from project root)
source venv311/bin/activate
uvicorn backend.app:app --reload

# Frontend (separate terminal)
cd frontend && npm run dev
```

Services: Frontend → http://localhost:3000 | Backend → http://localhost:8000 | Qdrant → http://localhost:6333 | Ollama → http://localhost:11434


## 1. Project Overview
Build a local Retrieval-Augmented Generation (RAG) pipeline that enables an LLM to answer questions using private local documents (PDFs, TXT, etc.) without data leaving your machine. Extend this with a web-based UI for document upload, ingestion, and chat. The backend will expose APIs for file management, ingestion, and chat, leveraging the existing Python codebase. Users can upload documents, select them in the chat interface, and ask questions based on their content.

## 2. Tech Stack
- **Inference Engine:** Ollama (Local LLM hosting)
- **LLM:** llama3 (via Ollama)
- **Embedding Model:** nomic-embed-text (via Ollama)
- **Vector Database:** Qdrant (Open-source, local persistence)
- **Orchestration:** LangChain or LlamaIndex
- **Backend:** Python (FastAPI), Ollama, Qdrant, LangChain
- **Frontend:** React (with Material UI or Chakra UI)

## 3. Implementation Phases

### Phase 1: Environment Setup
- **Install Ollama:** Ensure the service is running.
- **Download Models:**
    ```bash
    ollama pull llama3.1:8b(128K token) 
    ollama pull nomic-embed-text
    ```
- **Python Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Win
    pip install -r requirements.txt
    ```

### Phase 2: Backend API Development
- Expose REST APIs for:
  - File upload (PDF/TXT)
  - Document listing and selection
  - Ingestion trigger (embedding + Qdrant storage)
  - Chat endpoint (question answering based on selected document)
- Integrate existing ingest and chat logic as API endpoints.

### Phase 3: Frontend Web UI
- Build a web interface for:
  - Uploading documents
  - Viewing/selecting uploaded documents
  - Triggering ingestion
  - Chat interface (select document, ask questions, view answers)

### Phase 4: Retrieval & Generation (RAG)
- **Query Embedding:** Convert user questions into vectors using the same embedding model.
- **Similarity Search:** Retrieve the top 3–5 most relevant chunks from Qdrant.
- **Prompt Engineering:** Construct a prompt that forces the LLM to use only the retrieved context.
- **Response Generation:** Pass the prompt to llama3 via Ollama.

### Phase 5: Integration & Testing
- Connect frontend to backend APIs.
- Test end-to-end flow: upload → ingest → chat.
- Add error handling, logging, and user feedback.

### Phase 6: Enhancements
- User authentication (optional)
- Document metadata management
- Multi-document chat (combine context from multiple docs)
- UI improvements (history, file preview, etc.)

## 4. Directory Structure
```
local-rag-project/
├── backend/
│   ├── app.py           # FastAPI backend
│   ├── ingest.py        # Ingestion logic (reuse existing)
│   ├── chat.py          # Chat logic (reuse existing)
│   └── ...
├── frontend/
│   ├── src/
│   └── ...
├── data/                # Uploaded files
├── db/                  # Qdrant storage
├── venv/                # Python environment
└── requirements.txt     # Backend dependencies
```

## 5. Key Milestones
- **Milestone 1:** Successfully embed one PDF and save to Qdrant
- **Milestone 2:** Backend APIs for upload, ingestion, and chat
- **Milestone 3:** Web UI for document management and chat
- **Milestone 4:** Retrieve relevant text chunks based on a natural language query
- **Milestone 5:** End-to-end integration and testing
- **Milestone 6:** Advanced features and enhancements

## 6. Next Steps
- Review plan and finalize tech stack
- Start backend API development
- Build frontend UI
- Integrate and test

---

*Do not start implementation until plan is reviewed and approved.*
