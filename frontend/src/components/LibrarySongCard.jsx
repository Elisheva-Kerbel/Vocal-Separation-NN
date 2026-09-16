import { useState } from 'react'
import { statusBadgeClass, Icons, STEM_LABELS, STATUS_LABELS, VIS_LABELS } from '../helpers.jsx'
import { getListenUrl, getDownloadUrl } from '../api/songs.js'

export default function LibrarySongCard({ song, onPublish, onUnpublish, onDelete }) {
  const [listenUrls, setListenUrls] = useState({})
  const [error, setError] = useState('')

  async function loadListen(purpose) {
    try {
      const r = await getListenUrl(song.id, purpose)
      setListenUrls(prev => ({ ...prev, [purpose]: r.url }))
    } catch {
      setListenUrls(prev => ({ ...prev, [purpose]: `/songs/${song.id}/stream/${purpose}` }))
    }
  }

  async function onDownload(purpose) {
    try {
      const r = await getDownloadUrl(song.id, purpose)
      window.location.href = r.url
    } catch {
      const a = document.createElement('a')
      a.href = `/songs/${song.id}/stream/${purpose}`
      a.download = `${song.title || 'track'}_${purpose}.wav`
      a.click()
    }
  }

  return (
    <article className="song-card">
      <h3><a href={`#/song/${song.id}`}>{song.title || 'ללא שם'}</a></h3>
      <div style={{ display: 'flex', gap: '0.35rem', margin: '0.5rem 0', flexWrap: 'wrap' }}>
        <span className={statusBadgeClass(song.status)}>{STATUS_LABELS[song.status] || song.status}</span>
        <span className="badge neutral">{VIS_LABELS[song.visibility] || song.visibility}</span>
        {song.model_tier && <span className={`badge ${song.model_tier === 'professional' ? 'inst' : 'primary'} model-badge`}>
          {song.model_tier === 'professional' ? 'מקצועי' : 'בסיסי'}
        </span>}
      </div>
      <p className="hint">{new Date(song.created_at).toLocaleDateString('he-IL')}</p>

      {song.status === 'ready' && (
        <div className="song-card-stems">
          {['original', 'vocals', 'background'].map(purpose => (
            <div key={purpose} className="stem-row">
              <span className={`badge ${purpose === 'vocals' ? 'vocal' : purpose === 'background' ? 'inst' : 'neutral'}`} style={{ fontSize: '0.7rem', minWidth: '3rem', textAlign: 'center' }}>{STEM_LABELS[purpose] || 'מקור'}</span>
              {listenUrls[purpose] ? (
                <audio controls src={listenUrls[purpose]} style={{ flex: 1, height: 32 }} />
              ) : (
                <button className="ghost" style={{ fontSize: '0.75rem' }} onClick={() => loadListen(purpose)}>{Icons.headphones} האזן</button>
              )}
              <button className="ghost" style={{ fontSize: '0.75rem' }} onClick={() => onDownload(purpose)}>{Icons.download}</button>
            </div>
          ))}
        </div>
      )}

      {error && <p className="error" style={{ fontSize: '0.8rem' }}>{error}</p>}

      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
        {song.status === 'ready' && song.visibility === 'private' && (
          <button className="ghost" onClick={() => onPublish(song.id)}>{Icons.globe} פרסם</button>
        )}
        {song.visibility === 'public' && (
          <button className="ghost" onClick={() => onUnpublish(song.id)}>{Icons.eyeOff} הסר</button>
        )}
        <button className="ghost" style={{ color: 'var(--danger)' }} onClick={() => onDelete(song.id)}>{Icons.trash} מחק</button>
      </div>
    </article>
  )
}
