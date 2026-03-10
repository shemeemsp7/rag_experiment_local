import os
import uuid
import logging
from fastapi import HTTPException
from ingest import split_documents, embed_texts, client, COLLECTION_NAME, models
from langchain_community.document_loaders import PyPDFLoader, TextLoader
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

def ingest_file(filename, collection_name=None, metadata=None):
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
        # Prepare metadata
        meta = metadata or {}
        meta["filename"] = filename
        # Use provided collection name or default
        coll_name = collection_name or COLLECTION_NAME
        # Create collection if not exists
        collections = [c.name for c in client.get_collections().collections]
        if coll_name not in collections:
            logging.info(f"Creating collection '{coll_name}' in Qdrant...")
            client.create_collection(
                coll_name,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
            )
        # Add metadata to each chunk
        # Use deterministic UUIDs keyed on (collection, filename, index) so:
        # - re-ingesting the same file replaces the exact same points (idempotent)
        # - different files always get different IDs even in the same collection
        payload = [
            models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{coll_name}:{filename}:{i}")),
                vector=embeddings[i],
                payload={"text": texts[i], **meta}
            ) for i in range(len(texts))
        ]
        client.upsert(collection_name=coll_name, points=payload)
        logging.info(f"Ingested {len(texts)} chunks from file: {filename} into collection: {coll_name}")
        return len(texts)
    except HTTPException as he:
        logging.error(f"Ingestion error: {he.detail}")
        raise he
    except Exception as e:
        logging.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
