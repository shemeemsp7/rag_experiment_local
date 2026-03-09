import { useState, useRef, useEffect } from 'react'
import { chat } from '../api'

export default function ChatInterface({ documents, selected, onSelect, llmModel }) {
  const [question, setQuestion] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history])

  async function handleSend(e) {
    e.preventDefault()
    if (!selected) { setError('Select a document first.'); return }
    if (!question.trim()) return
    setError('')
    const q = question.trim()
    setQuestion('')
    setHistory(h => [...h, { role: 'user', text: q }])
    setLoading(true)
    try {
      const result = await chat(selected, q, llmModel)
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
        <label htmlFor="doc-select">Document:</label>
        <select
          id="doc-select"
          value={selected || ''}
          onChange={e => onSelect(e.target.value)}
          className="doc-select"
        >
          <option value="">-- select a document --</option>
          {documents.map(name => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
      </div>

      <div className="chat-history">
        {history.length === 0 && (
          <p className="empty-msg">Select a document and ask a question to get started.</p>
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
          placeholder="Ask a question about the selected document…"
          disabled={loading}
          className="chat-input"
        />
        <button type="submit" disabled={loading || !question.trim()} className="btn btn-primary">
          Send
        </button>
      </form>
    </div>
  )
}
