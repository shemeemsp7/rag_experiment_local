export async function listLLMModels() {
  const res = await fetch(`${BASE}/llm-models`)
  if (!res.ok) throw new Error('Failed to fetch LLM models')
  const data = await res.json()
  return data.models
}
export async function deleteDocument(filename) {
  const res = await fetch(`${BASE}/documents/${encodeURIComponent(filename)}`, { method: 'DELETE' })
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

export async function ingestDocument(filename) {
  const form = new FormData()
  form.append('filename', filename)
  const res = await fetch(`${BASE}/ingest`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Ingestion failed')
  }
  return res.json()
}

export async function chat(filename, question, model) {
  const form = new FormData()
  form.append('filename', filename)
  form.append('question', question)
  form.append('model', model)
  const res = await fetch(`${BASE}/chat`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Chat failed')
  }
  return res.json()
}
