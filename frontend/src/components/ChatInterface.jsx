import { useState, useRef, useEffect, useMemo } from 'react'
import { chat } from '../api'

export default function ChatInterface({ docsMetadata = [], selectedCollection, selectedTopic, onCollectionChange, onTopicChange, llmModel }) {
  const [question, setQuestion] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history])

  // Derive unique collections and topics from metadata
  const collections = useMemo(() => {
    const s = new Set(docsMetadata.map(d => d.collection).filter(Boolean))
    return [...s]
  }, [docsMetadata])

  const topics = useMemo(() => {
    const filtered = selectedCollection
      ? docsMetadata.filter(d => d.collection === selectedCollection)
      : docsMetadata
    const s = new Set(filtered.map(d => d.topic).filter(Boolean))
    return [...s]
  }, [docsMetadata, selectedCollection])

  // Reset topic when collection changes
  function handleCollectionChange(val) {
    onCollectionChange(val)
    onTopicChange('')
  }

  async function handleSend(e) {
    e.preventDefault()
    if (!selectedCollection) { setError('Select a collection first.'); return }
    if (!question.trim()) return
    setError('')
    const q = question.trim()
    setQuestion('')
    setHistory(h => [...h, { role: 'user', text: q }])
    setLoading(true)
    try {
      const result = await chat(q, llmModel, selectedCollection, selectedTopic)
      setHistory(h => [...h, { role: 'assistant', text: result.answer }])
    } catch (err) {
      setHistory(h => [...h, { role: 'error', text: err.message }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-container card">
      <h2>Chat</h2>

      <div className="chat-controls">
        <label htmlFor="col-select">Collection:</label>
        <select
          id="col-select"
          value={selectedCollection || ''}
          onChange={e => handleCollectionChange(e.target.value)}
          className="doc-select"
        >
          <option value="">-- select a collection --</option>
          {collections.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        {topics.length > 0 && (
          <>
            <label htmlFor="topic-select" style={{ marginLeft: 12 }}>Topic:</label>
            <select
              id="topic-select"
              value={selectedTopic || ''}
              onChange={e => onTopicChange(e.target.value)}
              className="doc-select"
            >
              <option value="">-- all topics --</option>
              {topics.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </>
        )}
      </div>

      <div className="chat-history">
        {history.length === 0 && (
          <p className="empty-msg">Select a collection and ask a question to get started.</p>
        )}
        {history.map((msg, i) => (
          <div key={i} className={`chat-bubble chat-bubble-${msg.role}`}>
            <span className="chat-role">{msg.role === 'user' ? 'You' : msg.role === 'error' ? 'Error' : 'Assistant'}</span>
            <p>{msg.text}</p>
          </div>
        ))}
        {loading && (
          <div className="chat-bubble chat-bubble-assistant">
            <span className="chat-role">Assistant</span>
            <p className="typing">Thinking…</p>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <p className="msg msg-error">{error}</p>}

      <form onSubmit={handleSend} className="chat-input-row">
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder={selectedCollection ? `Ask about ${selectedCollection}…` : 'Select a collection first…'}
          disabled={loading}
          className="chat-input"
        />
        <button type="submit" disabled={loading || !question.trim() || !selectedCollection} className="btn btn-primary">
          Send
        </button>
      </form>
    </div>
  )
}
