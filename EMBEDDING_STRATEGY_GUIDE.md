# Embedding Strategy Guide

## What This Repository Uses Today

This RAG project uses **dense semantic embeddings** at the **chunk level**.

- Embedding model: `nomic-embed-text` via Ollama
- Vector size: 768
- Similarity metric: cosine similarity
- Retrieval store: Qdrant
- Chunking: character-based chunks of 1000 with 100 overlap

In practical terms, the system does this:

1. Split each document into text chunks.
2. Convert each chunk into a dense vector embedding.
3. Convert the user query into a dense vector embedding using the same embedding model.
4. Search Qdrant for nearest vectors (top-k most similar chunks).
5. Send retrieved chunks as context to the LLM for answer generation.

This is **not** a word-to-word static vector lookup. It is **context-aware semantic retrieval** over chunks.

## Is It Word-to-Word or Context-Aware?

It is **context-aware** (semantic), not exact word matching only.

Example:

- Query: "best time to spray for fungal disease in corn"
- Retrieved chunk might say: "Apply fungicide around early tasseling stage in maize for better disease control."

Even if words are not identical (`corn` vs `maize`, `spray` vs `apply fungicide`), semantic embeddings can still place these texts close in vector space.

## Types of Embeddings and Retrieval (With Examples)

## 1) Static Word Embeddings

Examples: Word2Vec, GloVe, FastText

- One fixed vector per word.
- Same word always has same vector regardless of sentence.

Example:

- "bank" in "river bank" and "bank account" gets the same vector.

Pros:

- Fast, lightweight.

Cons:

- Weak handling of ambiguity and context.

## 2) Contextual Token Embeddings

Examples: BERT token embeddings

- Vector depends on surrounding words.
- Same token can have different vectors in different sentences.

Example:

- "bank" in finance sentence and river sentence gets different vectors.

Pros:

- Better context understanding.

Cons:

- More complex to use directly for large-scale retrieval.

## 3) Dense Sentence/Chunk Embeddings

Examples: `nomic-embed-text`, SBERT, E5, bge

- One vector for whole sentence/paragraph/chunk.
- Great for semantic search and RAG retrieval.

Example:

- "How to prevent leaf blight in rice?"
- Can match chunk: "Rice blast and blight prevention includes timely fungicide and field hygiene."

Pros:

- Strong semantic retrieval quality for RAG.

Cons:

- Can miss strict keyword constraints in some cases.

## 4) Sparse Lexical Retrieval

Examples: BM25, TF-IDF

- Scores based on token overlap and term statistics.
- Strong exact keyword precision.

Example:

- Query with unique part number often retrieves exact-match documents better than dense-only retrieval.

Pros:

- Excellent for exact-match terms.

Cons:

- Weak synonym and paraphrase understanding.

## 5) Hybrid Retrieval

Examples: dense + BM25 combined

- Uses semantic and lexical signals together.
- Often best practical production setup.

Pros:

- Balanced relevance and precision.

Cons:

- More system complexity and tuning.

## How to Think About This Project

Current approach in this repository is:

- **Dense semantic retrieval over chunks** (context-aware)
- **Not** pure lexical keyword search
- **Not** static word embedding lookup

If needed in future, hybrid retrieval can be added for stronger exact-term behavior while preserving semantic recall.

## Note About Code Comments

One comment/docstring in `ingest.py` mentions llama3.1:8b for embeddings, but the actual embedding calls use `nomic-embed-text`. The implementation is correct for semantic embedding; that wording is just stale documentation text.
