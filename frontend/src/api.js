export async function listLLMModels() {
  const res = await fetch(`${BASE}/llm-models`)
  if (!res.ok) throw new Error('Failed to fetch LLM models')
  const data = await res.json()
  return data.models
}
export async function deleteDocument(filename, collectionName) {
  const params = collectionName ? `?collection_name=${encodeURIComponent(collectionName)}` : ''
  const res = await fetch(`${BASE}/documents/${encodeURIComponent(filename)}${params}`, { method: 'DELETE' })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Delete failed')
  }
  return res.json()
}
const BASE = '/api'

export async function uploadDocument(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Upload failed')
  }
  return res.json()
}

export async function listDocuments() {
  const res = await fetch(`${BASE}/documents`)
  if (!res.ok) throw new Error('Failed to fetch documents')
  const data = await res.json()
  return data.documents
}

export async function ingestDocument(filename, collectionName, topic) {
  const form = new FormData()
  form.append('filename', filename)
  if (collectionName) form.append('collection_name', collectionName)
  if (topic) form.append('topic', topic)
  const res = await fetch(`${BASE}/ingest`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Ingestion failed')
  }
  return res.json()
}

export async function listCollections() {
  const res = await fetch(`${BASE}/collections`)
  if (!res.ok) throw new Error('Failed to fetch collections')
  const data = await res.json()
  return data.collections
}

export async function getCollectionDetails(name) {
  const res = await fetch(`${BASE}/collection/${encodeURIComponent(name)}`)
  if (!res.ok) throw new Error('Failed to fetch collection details')
  return res.json()
}

export async function searchCollection(collectionName, queryVector, metadataFilters, topK = 5) {
  const form = new FormData()
  form.append('collection_name', collectionName)
  form.append('top_k', topK)
  // Use fetch with body for queryVector and metadataFilters
  const body = {
    query_vector,
    metadata_filters: metadataFilters || {}
  }
  const res = await fetch(`${BASE}/search`, {
    method: 'POST',
    body: JSON.stringify(body),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  if (!res.ok) throw new Error('Search failed')
  return res.json()
}

export async function listDocumentsWithMetadata() {
  const res = await fetch(`${BASE}/documents/info`)
  if (!res.ok) throw new Error('Failed to fetch document metadata')
  const data = await res.json()
  return data.documents // [{filename, collection, topic}]
}

export async function chat(question, model, collectionName, topic) {
  const form = new FormData()
  form.append('question', question)
  form.append('model', model || 'llama3.1:8b')
  if (collectionName) form.append('collection_name', collectionName)
  if (topic) form.append('topic', topic)
  const res = await fetch(`${BASE}/chat`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Chat failed')
  }
  return res.json()
}
