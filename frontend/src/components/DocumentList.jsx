

import { useState } from 'react'
import { deleteDocument } from '../api'

export default function DocumentList({ docsMetadata = [], selected, onSelect, onRefresh }) {
  const [deleteStatus, setDeleteStatus] = useState({})

  async function handleDelete(filename, collection) {
    setDeleteStatus(s => ({ ...s, [filename]: { loading: true, msg: '', error: '' } }))
    try {
      const result = await deleteDocument(filename, collection)
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

  return (
    <div className="card">
      <div className="card-header">
        <h2>Documents</h2>
        <button onClick={onRefresh} className="btn btn-outline">Refresh</button>
      </div>
      {docsMetadata.length === 0 ? (
        <p className="empty-msg">No documents yet. Upload one above.</p>
      ) : (
        <ul className="doc-list">
          {docsMetadata.map(({ filename, collection, topic }) => {
            const isSelected = selected === filename
            const ds = deleteStatus[filename] || {}
            return (
              <li
                key={filename}
                className={`doc-item ${isSelected ? 'doc-item-selected' : ''}`}
                onClick={() => onSelect(filename, collection, topic)}
                title="Click to select for chat"
              >
                <div className="doc-item-main">
                  <span className="doc-name">{filename}</span>
                  <div className="doc-badges">
                    {collection && <span className="badge badge-collection">{collection}</span>}
                    {topic && <span className="badge badge-topic">{topic}</span>}
                  </div>
                </div>
                <div className="doc-actions">
                  <button
                    className="btn btn-sm btn-error"
                    disabled={ds.loading}
                    onClick={e => { e.stopPropagation(); handleDelete(filename, collection) }}
                  >
                    {ds.loading ? 'Deleting…' : 'Delete'}
                  </button>
                </div>
                {ds.msg && <span className="doc-status msg-success">{ds.msg}</span>}
                {ds.error && <span className="doc-status msg-error">{ds.error}</span>}
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )

}