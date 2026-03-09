"""
Chat with your data using RAG and llama3.1:8b via Ollama.
"""
from qdrant_client import QdrantClient
import ollama
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "rag_docs"

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def get_query_embedding(query):
    logging.info("Generating embedding for query...")
    embedding = ollama.embeddings(model="nomic-embed-text", prompt=query)["embedding"]
    logging.info("Query embedding generated.")
    return embedding

def retrieve_context(query_embedding, top_k=5):
    logging.info(f"Retrieving top {top_k} relevant chunks from Qdrant...")
    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    ).points
    logging.info(f"Retrieved {len(search_result)} chunks.")
    return [hit.payload["text"] for hit in search_result]

def build_prompt(context, question):
    context_str = "\n---\n".join(context)
    prompt = f"Answer the question using only the context below.\nContext:\n{context_str}\n\nQuestion: {question}\nAnswer:"
    logging.info("Prompt constructed for LLM.")
    return prompt

def main():
    logging.info("Starting chat interface...")
    while True:
        question = input("Ask a question (or 'exit'): ")
        if question.lower() == "exit":
            logging.info("Exiting chat interface.")
            break
        logging.info(f"Received question: {question}")
        query_embedding = get_query_embedding(question)
        context = retrieve_context(query_embedding)
        prompt = build_prompt(context, question)
        logging.info("Generating response from LLM...")
        response = ollama.generate(model="llama3.1:8b", prompt=prompt)["response"]
        logging.info("Response generated.")
        print(f"\nResponse:\n{response}\n")

if __name__ == "__main__":
    main()
