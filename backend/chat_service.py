import os
import ollama
import logging
from fastapi import HTTPException
from chat import get_query_embedding, retrieve_context, build_prompt
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from ingest import split_documents, embed_texts, client, COLLECTION_NAME, models
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

def chat_with_file(filename, question, model="llama3.1:8b"):
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
        query_embedding = get_query_embedding(question)
        context = retrieve_context(query_embedding)
        prompt = build_prompt(context, question)
        response = ollama.generate(model=model, prompt=prompt)["response"]
        logging.info(f"Chat answer generated for file: {filename}, question: '{question}', model: '{model}'")
        return response
    except HTTPException as he:
        logging.error(f"Chat error: {he.detail}")
        raise he
    except Exception as e:
        logging.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")
