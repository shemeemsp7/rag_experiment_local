

import { useState } from 'react'
import { ingestDocument, deleteDocument } from '../api'

export default function DocumentList({ documents, selected, onSelect, onRefresh }) {
  const [ingestStatus, setIngestStatus] = useState({})
  const [deleteStatus, setDeleteStatus] = useState({})

  async function handleDelete(filename) {
    setDeleteStatus(s => ({ ...s, [filename]: { loading: true, msg: '', error: '' } }))
    try {
      const result = await deleteDocument(filename)
      setDeleteStatus(s => ({
        ...s,
        [filename]: { loading: false, msg: result.status, error: '' }
      }))
      onRefresh()
    } catch (err) {
      setDeleteStatus(s => ({
        ...s,
        [filename]: { loading: false, msg: '', error: err.message }
      }))
    }
  }

  async function handleIngest(filename) {
    setIngestStatus(s => ({ ...s, [filename]: { loading: true, msg: '', error: '' } }))
    try {
      const result = await ingestDocument(filename)
      setIngestStatus(s => ({
        ...s,
        [filename]: { loading: false, msg: result.status, error: '' }
      }))
    } catch (err) {
      setIngestStatus(s => ({
        ...s,
        [filename]: { loading: false, msg: '', error: err.message }
      }))
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Documents</h2>
        <button onClick={onRefresh} className="btn btn-outline">Refresh</button>
      </div>
      {documents.length === 0 ? (
        <p className="empty-msg">No documents yet. Upload one above.</p>
      ) : (
        <ul className="doc-list">
          {documents.map(name => {
            const st = ingestStatus[name] || {}
            const isSelected = selected === name
            return (
              <li
                key={name}
                className={`doc-item ${isSelected ? 'doc-item-selected' : ''}`}
              >
                <span
                  className="doc-name"
                  onClick={() => onSelect(name)}
                  title="Select for chat"
                >
                  {name}
                </span>
                <div className="doc-actions">
                  <button
                    className="btn btn-sm btn-outline"
                    disabled={st.loading}
                    onClick={() => handleIngest(name)}
                  >
                    {st.loading ? 'Ingesting…' : 'Ingest'}
                  </button>
                  <button
                    className="btn btn-sm btn-error"
                    disabled={deleteStatus[name]?.loading}
                    onClick={() => handleDelete(name)}
                  >
                    {deleteStatus[name]?.loading ? 'Deleting…' : 'Delete'}
                  </button>
                </div>
                {deleteStatus[name]?.msg && <span className="doc-status msg-success">{deleteStatus[name].msg}</span>}
                {deleteStatus[name]?.error && <span className="doc-status msg-error">{deleteStatus[name].error}</span>}
                {st.msg && <span className="doc-status msg-success">{st.msg}</span>}
                {st.error && <span className="doc-status msg-error">{st.error}</span>}
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )

}