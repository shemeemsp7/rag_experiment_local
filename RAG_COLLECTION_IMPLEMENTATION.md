# RAG Pipeline Enhancement Plan: Per-File/Topic Collections & Metadata

## Backend (Python/FastAPI)

### 1. Ingestion Logic
- Allow specifying collection name (file/topic) when uploading documents.
- If collection does not exist, create it; else, append to existing collection.
- Add metadata (filename, topic, etc.) to each chunk’s payload for improved filtering.

### 2. API Endpoints
- `POST /upload`: Accept file, collection name/topic, and metadata.
- `GET /collections`: List all collections.
- `GET /collection/{name}`: Retrieve collection details.
- `POST /search`: Search within a specific collection, with optional metadata filters.

### 3. Qdrant Interaction
- Dynamically create/use collections based on file/topic.
- Store metadata in payload for filtering during retrieval.

---

## Frontend (React/Vite)

### 1. Document Upload UI
- Allow user to select or create a collection (dropdown or input).
- Upload file with collection name/topic and metadata.

### 2. Collection Management UI
- List existing collections.
- Option to view, search, or delete collections.

### 3. Search UI
- Allow searching within a selected collection.
- Optionally filter by metadata (filename, topic).

---

## Implementation Notes
- Ensure backend and frontend are aligned for collection and metadata handling.
- Use metadata for more precise retrieval and filtering in Qdrant.
- Provide clear UI for collection selection/creation and search filtering.

---

This plan guides the implementation of per-file/topic collections and metadata support for improved retrieval in your RAG pipeline.
