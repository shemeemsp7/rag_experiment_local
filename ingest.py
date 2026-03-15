"""
Ingest documents, generate embeddings using nomic-embed-text, llama3.1:8b via Ollama, and store in Qdrant.
"""
import os
from qdrant_client import QdrantClient, models
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
import ollama
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

DATA_DIR = "data"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "rag_docs"

logging.info("Initializing Qdrant client...")
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
collections = [c.name for c in client.get_collections().collections]
if COLLECTION_NAME not in collections:
    logging.info(f"Creating collection '{COLLECTION_NAME}' in Qdrant...")
    client.create_collection(
        COLLECTION_NAME,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
    )
else:
    logging.info(f"Collection '{COLLECTION_NAME}' already exists.")

def load_documents(data_dir):
    logging.info(f"Loading documents from '{data_dir}'...")
    docs = []
    for fname in os.listdir(data_dir):
        fpath = os.path.join(data_dir, fname)
        if fname.lower().endswith(".pdf"):
            logging.info(f"Loading PDF: {fname}")
            docs.extend(PyPDFLoader(fpath).load())
        elif fname.lower().endswith(".txt"):
            logging.info(f"Loading TXT: {fname}")
            docs.extend(TextLoader(fpath).load())
    logging.info(f"Loaded {len(docs)} documents.")
    return docs

def split_documents(docs):
    logging.info("Splitting documents into chunks...")
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    logging.info(f"Split into {len(chunks)} chunks.")
    return chunks

def embed_texts(texts):
    logging.info("Generating embeddings for chunks using nomic-embed-text...")
    embeddings = []
    for idx, t in enumerate(texts):
        logging.info(f"Embedding chunk {idx+1}/{len(texts)}")
        embeddings.append(ollama.embeddings(model="nomic-embed-text", prompt=t)["embedding"])
    logging.info("Embeddings generated.")
    return embeddings

def main():
    logging.info("Starting ingestion pipeline...")
    docs = load_documents(DATA_DIR)
    chunks = split_documents(docs)
    texts = [chunk.page_content for chunk in chunks]
    embeddings = embed_texts(texts)
    logging.info("Preparing payload for Qdrant...")
    payload = [
        models.PointStruct(
            id=i,
            vector=embeddings[i],
            payload={"text": texts[i]}
        ) for i in range(len(texts))
    ]
    logging.info(f"Uploading {len(payload)} points to Qdrant...")
    client.upsert(collection_name=COLLECTION_NAME, points=payload)
    logging.info(f"Ingested {len(texts)} chunks into Qdrant.")

if __name__ == "__main__":
    main()
