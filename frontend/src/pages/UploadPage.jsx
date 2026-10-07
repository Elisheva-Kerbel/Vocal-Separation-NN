import { useState } from 'react'
import { Icons } from '../helpers.jsx'
import { uploadSong } from '../api/songs.js'

export default function UploadPage({ user, quota, onUploaded, t }) {
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [modelChoice, setModelChoice] = useState(user.tier === 'pro' ? 'professional' : 'basic')
  const [visibility, setVisibility] = useState('private')

  const proQuotaLeft = quota && quota.professional_limit ? quota.professional_limit - quota.professional_used : 0
  const canPickPro = user.tier === 'pro' && proQuotaLeft > 0

  async function onUpload() {
    if (!file) return
    setBusy(true); setError(''); setProgress(0)
    try {
      const res = await uploadSong(file, setProgress, { modelChoice, visibility })
      onUploaded()
      window.location.hash = `#/song/${res.song_id}`
    } catch (f) { setError(f.message) }
    finally { setBusy(false) }
  }

  return (
    <section className="page-section">
      <div className="wrap" style={{ maxWidth: '36rem' }}>
        <h2>{t('upload')}</h2>
        <p className="lede" style={{ margin: '0.5rem 0 1.5rem' }}>MP3, WAV או M4A · עד 100 MB · מקסימום 5.5 דקות</p>
        <div className="panel">
          {error && <p className="error" role="alert">{error}</p>}
          <label className="drop">
            <input type="file" accept="audio/mpeg,audio/wav,audio/mp4,.mp3,.wav,.m4a" onChange={e => setFile(e.target.files[0])} />
            <span className="drop-icon">{Icons.upload}</span>
            <b>{file ? file.name : 'בחר קובץ'}</b>
            {file && <span className="hint">{(file.size / 1024 / 1024).toFixed(1)} MB</span>}
          </label>

          <div className="upload-options">
            <div className="option-group">
              <span className="option-label">רמת הפרדה</span>
              <div className="segmented" role="radiogroup">
                <button type="button" role="radio" aria-checked={modelChoice === 'basic'}
                  className={`seg ${modelChoice === 'basic' ? 'on' : ''}`}
                  onClick={() => setModelChoice('basic')}>בסיסי</button>
                <button type="button" role="radio" aria-checked={modelChoice === 'professional'}
                  className={`seg ${modelChoice === 'professional' ? 'on' : ''} ${!canPickPro ? 'disabled' : ''}`}
                  disabled={!canPickPro}
                  onClick={() => canPickPro && setModelChoice('professional')}>
                  מקצועי {user.tier !== 'pro' && <span className="badge inst" style={{ fontSize: '0.65rem', marginRight: '0.25rem' }}>Pro</span>}
                </button>
              </div>
              {user.tier === 'pro' && quota && (
                <span className="hint" style={{ fontSize: '0.75rem' }}>נותרו {proQuotaLeft} הפרדות מקצועיות היום</span>
              )}
              {user.tier !== 'pro' && (
                <span className="hint" style={{ fontSize: '0.75rem' }}>הפרדה מקצועית זמינה <a href="#/upgrade" className="link">למנויי Pro</a></span>
              )}
            </div>

            <div className="option-group">
              <span className="option-label">נראות</span>
              <div className="segmented" role="radiogroup">
                <button type="button" role="radio" aria-checked={visibility === 'private'}
                  className={`seg ${visibility === 'private' ? 'on' : ''}`}
                  onClick={() => setVisibility('private')}>פרטי</button>
                <button type="button" role="radio" aria-checked={visibility === 'public'}
                  className={`seg ${visibility === 'public' ? 'on' : ''}`}
                  onClick={() => setVisibility('public')}>ציבורי</button>
              </div>
            </div>
          </div>

          {busy && <div style={{ marginTop: '1rem' }}>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
            <p className="hint">{progress}% הועלה</p>
          </div>}
          <button className="btn full" type="button" disabled={!file || busy} onClick={onUpload} style={{ marginTop: '1rem' }}>
            {busy ? 'מעלה...' : 'העלה והפרד'}
          </button>
        </div>
      </div>
    </section>
  )
}
