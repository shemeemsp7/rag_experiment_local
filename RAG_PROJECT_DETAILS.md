
# Project Plan: Local RAG Implementation & Web UI Extension (Qdrant)

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
