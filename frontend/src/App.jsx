import React, { useState, useEffect, useCallback } from 'react'
import DocumentUpload from './components/DocumentUpload'
import DocumentList from './components/DocumentList'
import ChatInterface from './components/ChatInterface'
import { listDocuments, listLLMModels } from './api'

export default function App() {
  const [documents, setDocuments] = useState([])
  const [selected, setSelected] = useState('')
  const [loadError, setLoadError] = useState('')
  const [llmModels, setLLMModels] = useState([])
  const [chosenModel, setChosenModel] = useState(() => localStorage.getItem('llmModel') || 'llama3.1:8b')

  const fetchDocuments = useCallback(async () => {
    try {
      const docs = await listDocuments()
      setDocuments(docs)
      setLoadError('')
    } catch (err) {
      setLoadError('Could not load documents: ' + err.message)
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
    listLLMModels().then(setLLMModels).catch(() => {})
  }, [fetchDocuments])

  return (
    <div className="app">
      <header className="app-header">
        <h1>RAG Document Assistant</h1>
        <span className="app-subtitle">Upload, ingest, and chat with your documents locally</span>
        <div className="llm-select-row">
          <label htmlFor="llm-select">Choose LLM Model:</label>
          <select
            id="llm-select"
            value={chosenModel}
            onChange={e => {
              setChosenModel(e.target.value)
              localStorage.setItem('llmModel', e.target.value)
            }}
            className="llm-select"
          >
            {llmModels.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
      </header>

      <main className="app-layout">
        <aside className="sidebar">
          <DocumentUpload onUpload={fetchDocuments} />
          {loadError && <p className="msg msg-error">{loadError}</p>}
          <DocumentList
            documents={documents}
            onRefresh={fetchDocuments}
            onSelect={setSelected}
            selected={selected}
          />
        </aside>

        <section className="main-panel">
          <ChatInterface
            documents={documents}
            selected={selected}
            onSelect={setSelected}
            llmModel={chosenModel}
          />
        </section>
      </main>
    </div>
  )
}
