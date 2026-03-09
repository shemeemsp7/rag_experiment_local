import { useState, useRef } from 'react'
import { uploadDocument } from '../api'

export default function DocumentUpload({ onUpload }) {
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const inputRef = useRef()

  async function handleUpload(e) {
    e.preventDefault()
    const file = inputRef.current?.files[0]
    console.log('handleUpload called, file:', file)
    if (!file) {
      setError('No file selected.')
      console.warn('No file selected.')
      return
    }
    setLoading(true)
    setStatus('')
    setError('')
    try {
      console.log('Uploading file:', file.name)
      await uploadDocument(file)
      setStatus(`"${file.name}" uploaded successfully.`)
      inputRef.current.value = ''
      onUpload()
    } catch (err) {
      setError(err.message)
      console.error('Upload error:', err)
    } finally {
      setLoading(false)
      console.log('Upload finished')
    }
  }

  return (
    <div className="card">
      <h2>Upload Document</h2>
      <form onSubmit={handleUpload} className="upload-form">
        <label htmlFor="file-upload" className="file-input-label">
          Choose File
        </label>
        <span id="file-selected-log" style={{fontSize: '0.85em', color: '#64748b', marginRight: '10px'}}>
          {inputRef.current?.files && inputRef.current.files[0] ? `Selected: ${inputRef.current.files[0].name}` : ''}
        </span>
        <input
          ref={inputRef}
          id="file-upload"
          type="file"
          accept=".pdf,.txt"
          className="file-input"
        />
        <button type="submit" disabled={loading} className="btn btn-primary">
          {loading ? 'Uploading…' : 'Upload'}
        </button>
      </form>
      {status && <p className="msg msg-success">{status}</p>}
      {error && <p className="msg msg-error">{error}</p>}
    </div>
  )
}
