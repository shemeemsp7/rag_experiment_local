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

@app.delete("/documents/{filename}", status_code=status.HTTP_200_OK)
async def delete_document(filename: str, request: Request = None):
    file_path = os.path.join(UPLOAD_DIR, filename)
    logging.info(f"DELETE /documents/{filename} from {request.client.host if request else 'unknown'}")
    # Delete file
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"Deleted file: {file_path}")
    else:
        logging.warning(f"File not found for deletion: {file_path}")
    # Delete vectors from Qdrant
    try:
        points_selector = Filter(must=[FieldCondition(key="text", match={"value": filename})])
        client.delete(collection_name=COLLECTION_NAME, points_selector=points_selector)
        logging.info(f"Deleted vectors for file: {filename}")
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

@app.post("/ingest")
async def ingest_document(filename: str = Form(...), request: Request = None):
    logging.info(f"POST /ingest from {request.client.host if request else 'unknown'} filename={filename}")
    chunk_count = ingest_file(filename)
    logging.info(f"Ingested {chunk_count} chunks from {filename}")
    return {"filename": filename, "status": f"Ingested {chunk_count} chunks"}

@app.post("/chat")
async def chat_with_document(
    filename: str = Form(...),
    question: str = Form(...),
    model: str = Form("llama3.1:8b"),
    request: Request = None
):
    logging.info(f"POST /chat from {request.client.host if request else 'unknown'} filename={filename} question={question} model={model}")
    answer = chat_with_file(filename, question, model)
    logging.info(f"Chat answer for {filename}: {answer}")
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
