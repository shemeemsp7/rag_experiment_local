import { useState, useRef, useEffect } from 'react'
import { uploadDocument, ingestDocument, listCollections } from '../api'

export default function DocumentUpload({ onUpload }) {
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const inputRef = useRef()
  const [selectedFile, setSelectedFile] = useState(null)
  const [collectionName, setCollectionName] = useState('')
  const [topic, setTopic] = useState('')
  const [collections, setCollections] = useState([])

  useEffect(() => {
    listCollections().then(setCollections).catch(() => {})
  }, [])

  async function handleUpload(e) {
    e.preventDefault()
    const file = inputRef.current?.files[0]
    if (!file) {
      setError('No file selected.')
      return
    }
    if (!collectionName) {
      setError('Please select or enter a collection name.')
      return
    }
    setLoading(true)
    setStatus('')
    setError('')
    try {
      // Upload file
      const uploadResult = await uploadDocument(file)
      const filename = uploadResult.filename
      setStatus(`"${file.name}" uploaded. Ingesting into "${collectionName}"…`)
      // Ingest into the selected/new collection
      await ingestDocument(filename, collectionName, topic)
      setStatus(`"${file.name}" uploaded and ingested into collection "${collectionName}".`)
      inputRef.current.value = ''
      setSelectedFile(null)
      onUpload()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
  
    function handleFileChange(e) {
      setSelectedFile(e.target.files[0] || null)
    }

  return (
    <div className="card">
      <h2>Upload Document</h2>
      <form onSubmit={handleUpload} className="upload-form" style={{display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '10px'}}>
        <div className="collection-controls" style={{marginBottom: 0}}>
          <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
            <label style={{ marginBottom: 4 }}>
              Collection Name:
              <select
                value={collectionName}
                onChange={e => setCollectionName(e.target.value)}
                className="input input-sm"
                style={{ marginLeft: 8, minWidth: 140 }}
              >
                <option value="">-- New Collection --</option>
                {collections.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </label>
            <input
              type="text"
              value={collectionName}
              onChange={e => setCollectionName(e.target.value)}
              placeholder="Or enter new collection"
              className="input input-sm"
              style={{ marginLeft: 8, marginTop: 2, minWidth: 140 }}
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
            <label style={{ marginBottom: 4 }}>
              Topic:
              <input
                type="text"
                value={topic}
                onChange={e => setTopic(e.target.value)}
                placeholder="Optional topic/tag"
                className="input input-sm"
                style={{ marginLeft: 8, minWidth: 140 }}
              />
            </label>
          </div>
        </div>
        <label htmlFor="file-upload" className="file-input-label">
          Choose File
        </label>
        <span
          id="file-selected-log"
          style={{
            fontSize: '0.85em',
            color: selectedFile ? '#15803d' : '#64748b',
            background: selectedFile ? '#dcfce7' : 'transparent',
            marginRight: '10px',
            minWidth: '180px',
            maxWidth: '220px',
            display: 'inline-block',
            padding: selectedFile ? '2px 8px' : '0',
            borderRadius: selectedFile ? '8px' : '0',
            transition: 'background 0.2s, color 0.2s',
            textOverflow: 'ellipsis',
            overflow: 'hidden',
            whiteSpace: 'nowrap'
          }}
        >
          {selectedFile ? `Selected: ${selectedFile.name}` : ''}
        </span>
        <input
          ref={inputRef}
          id="file-upload"
          type="file"
          accept=".pdf,.txt"
          className="file-input"
          onChange={handleFileChange}
        />
        <div style={{flex: '1 0 auto'}}></div>
        <button type="submit" disabled={loading} className="btn btn-primary" style={{marginLeft: 'auto'}}>
          {loading ? 'Uploading…' : 'Upload'}
        </button>
      </form>
      {status && <p className="msg msg-success">{status}</p>}
      {error && <p className="msg msg-error">{error}</p>}
    </div>
  )
}
