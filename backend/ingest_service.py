import os
import logging
from fastapi import HTTPException
from ingest import split_documents, embed_texts, client, COLLECTION_NAME, models
from langchain_community.document_loaders import PyPDFLoader, TextLoader
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

def ingest_file(filename):
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        docs = []
        if filename.lower().endswith(".pdf"):
            docs.extend(PyPDFLoader(file_path).load())
        elif filename.lower().endswith(".txt"):
            docs.extend(TextLoader(file_path).load())
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        chunks = split_documents(docs)
        texts = [chunk.page_content for chunk in chunks]
        embeddings = embed_texts(texts)
        payload = [
            models.PointStruct(
                id=i,
                vector=embeddings[i],
                payload={"text": texts[i]}
            ) for i in range(len(texts))
        ]
        client.upsert(collection_name=COLLECTION_NAME, points=payload)
        logging.info(f"Ingested {len(texts)} chunks from file: {filename}")
        return len(texts)
    except HTTPException as he:
        logging.error(f"Ingestion error: {he.detail}")
        raise he
    except Exception as e:
        logging.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
