import ollama
import logging
from fastapi import HTTPException
from chat import get_query_embedding, build_prompt
from ingest import client, COLLECTION_NAME, models

def chat_with_file(filename, question, model="llama3.1:8b", collection_name=None, topic=None):
    try:
        query_embedding = get_query_embedding(question)
        coll = collection_name or COLLECTION_NAME

        must_conditions = []
        if filename:
            must_conditions.append(
                models.FieldCondition(key="filename", match=models.MatchValue(value=filename))
            )
        if topic:
            must_conditions.append(
                models.FieldCondition(key="topic", match=models.MatchValue(value=topic))
            )
        qdrant_filter = models.Filter(must=must_conditions) if must_conditions else None

        search_result = client.query_points(
            collection_name=coll,
            query=query_embedding,
            limit=5,
            query_filter=qdrant_filter
        ).points

        context = [hit.payload["text"] for hit in search_result]
        if not context:
            return "No relevant context found in the selected collection."

        prompt = build_prompt(context, question)
        response = ollama.generate(model=model, prompt=prompt)["response"]
        logging.info(f"Chat generated for collection={coll}, question='{question}', model={model}")
        return response
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")
