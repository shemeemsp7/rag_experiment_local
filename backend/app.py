# --- Search Endpoint ---
from fastapi import Body
from qdrant_client.http.models.models import Filter, FieldCondition
import ollama
import logging
from fastapi import FastAPI, UploadFile, File, Form, Request, status
from fastapi.responses import JSONResponse
from typing import List
from backend.file_service import save_file, list_files, UPLOAD_DIR
from backend.ingest_service import ingest_file
from backend.chat_service import chat_with_file
from ingest import client, COLLECTION_NAME
from qdrant_client.http.models.models import Filter, FieldCondition
import os

logging.basicConfig(level=logging.INFO)
app = FastAPI()

from ingest import client as qdrant_client

@app.post("/search")
async def search_collection(
    collection_name: str = Form(...),
    query_vector: List[float] = Body(...),
    metadata_filters: dict = Body(None),
    top_k: int = Form(5),
    request: Request = None
):
    logging.info(f"POST /search from {request.client.host if request else 'unknown'} collection={collection_name} filters={metadata_filters}")
    try:
        # Build filter conditions
        filter_conditions = []
        if metadata_filters:
            for key, value in metadata_filters.items():
                filter_conditions.append(FieldCondition(key=key, match={"value": value}))
        qdrant_filter = Filter(must=filter_conditions) if filter_conditions else None
        # Perform search
        search_result = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            filter=qdrant_filter
        )
        return {"results": [r.dict() for r in search_result]}  
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/collections")
async def list_collections(request: Request = None):
    logging.info(f"GET /collections from {request.client.host if request else 'unknown'}")
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        return {"collections": collection_names}
    except Exception as e:
        logging.error(f"Failed to list collections: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/collection/{name}")
async def get_collection_details(name: str, request: Request = None):
    logging.info(f"GET /collection/{name} from {request.client.host if request else 'unknown'}")
    try:
        info = qdrant_client.get_collection(name)
        return {"collection": name, "info": info.dict()}
    except Exception as e:
        logging.error(f"Failed to get collection details: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/documents/{filename}", status_code=status.HTTP_200_OK)
async def delete_document(filename: str, collection_name: str = None, request: Request = None):
    file_path = os.path.join(UPLOAD_DIR, filename)
    logging.info(f"DELETE /documents/{filename} collection={collection_name} from {request.client.host if request else 'unknown'}")
    # Delete file from disk
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"Deleted file: {file_path}")
    else:
        logging.warning(f"File not found for deletion: {file_path}")
    # Delete vectors from Qdrant
    # Build the correct payload filter: match on 'filename' field (not 'text')
    point_filter = Filter(must=[FieldCondition(key="filename", match={"value": filename})])
    try:
        all_collections = [c.name for c in qdrant_client.get_collections().collections]
        # If caller specified a collection, only operate on that one;
        # otherwise scan every collection (handles legacy data or missing param)
        target_collections = [collection_name] if collection_name and collection_name in all_collections else all_collections
        for coll in target_collections:
            try:
                # Delete only the points that belong to this specific file
                qdrant_client.delete(
                    collection_name=coll,
                    points_selector=point_filter
                )
                logging.info(f"Deleted vectors for '{filename}' from collection '{coll}'")
                # Check if the collection is now empty; delete it if so
                remaining = qdrant_client.count(collection_name=coll, exact=True).count
                if remaining == 0:
                    qdrant_client.delete_collection(coll)
                    logging.info(f"Collection '{coll}' is now empty — deleted it")
            except Exception as col_err:
                logging.warning(f"Could not clean up collection '{coll}': {col_err}")
    except Exception as e:
        logging.error(f"Qdrant delete error: {e}")
    return {"status": "deleted", "filename": filename}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), request: Request = None):
    logging.info(f"POST /upload from {request.client.host if request else 'unknown'}")
    filename = save_file(file)
    logging.info(f"Uploaded file: {filename}")
    return {"filename": filename, "status": "uploaded"}

@app.get("/documents")
async def list_documents(request: Request = None):
    logging.info(f"GET /documents from {request.client.host if request else 'unknown'}")
    files = list_files()
    logging.info(f"Documents listed: {files}")
    return {"documents": files}

@app.get("/documents/info")
async def list_documents_info(request: Request = None):
    """Returns each document with its collection and topic scraped from Qdrant payloads."""
    logging.info(f"GET /documents/info from {request.client.host if request else 'unknown'}")
    try:
        collections = qdrant_client.get_collections().collections
        doc_info = {}  # filename -> {collection, topic}
        for col in collections:
            try:
                offset = None
                while True:
                    records, offset = qdrant_client.scroll(
                        collection_name=col.name,
                        limit=100,
                        offset=offset,
                        with_payload=True,
                        with_vectors=False
                    )
                    for record in records:
                        payload = record.payload or {}
                        fname = payload.get("filename")
                        topic = payload.get("topic") or ""
                        if fname and fname not in doc_info:
                            doc_info[fname] = {"collection": col.name, "topic": topic}
                    if offset is None:
                        break
            except Exception as col_err:
                logging.warning(f"Could not scroll collection {col.name}: {col_err}")
                continue
        return {"documents": [{"filename": k, **v} for k, v in doc_info.items()]}
    except Exception as e:
        logging.error(f"Failed to get documents info: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ingest")
async def ingest_document(
    filename: str = Form(...),
    collection_name: str = Form(None),
    topic: str = Form(None),
    request: Request = None
):
    logging.info(f"POST /ingest from {request.client.host if request else 'unknown'} filename={filename} collection={collection_name} topic={topic}")
    metadata = {"topic": topic} if topic else {}
    chunk_count = ingest_file(filename, collection_name=collection_name, metadata=metadata)
    logging.info(f"Ingested {chunk_count} chunks from {filename} into collection {collection_name or COLLECTION_NAME}")
    return {"filename": filename, "collection": collection_name or COLLECTION_NAME, "status": f"Ingested {chunk_count} chunks"}

@app.post("/chat")
async def chat_with_document(
    filename: str = Form(""),
    question: str = Form(...),
    model: str = Form("llama3.1:8b"),
    collection_name: str = Form(None),
    topic: str = Form(None),
    request: Request = None
):
    logging.info(f"POST /chat from {request.client.host if request else 'unknown'} filename={filename} question={question} model={model} collection={collection_name} topic={topic}")
    answer = chat_with_file(filename or None, question, model, collection_name=collection_name, topic=topic)
    return {"filename": filename, "question": question, "model": model, "answer": answer}

@app.get("/llm-models")
async def list_llm_models(request: Request = None):
    logging.info(f"GET /llm-models from {request.client.host if request else 'unknown'}")
    try:
        models = ollama.list().models
        model_names = [m.model for m in models]
        return {"models": model_names}
    except Exception as e:
        logging.error(f"Failed to list LLM models: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def root(request: Request = None):
    logging.info(f"GET / from {request.client.host if request else 'unknown'}")
    return JSONResponse({"status": "RAG API running"})
