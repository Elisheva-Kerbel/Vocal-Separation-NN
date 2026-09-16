import { useState } from 'react'
import { Icons } from '../helpers.jsx'
import { getPublicListenUrl } from '../api/songs.js'

export default function PublicSongCard({ song: s, user, onRate, t }) {
  const [expanded, setExpanded] = useState(false)
  const [urls, setUrls] = useState({})

  async function loadPublicUrls() {
    if (expanded) { setExpanded(false); return }
    setExpanded(true)
    for (const p of ['original', 'vocals', 'background']) {
      if (urls[p]) continue
      try {
        const data = await getPublicListenUrl(s.id, p)
        setUrls(prev => ({ ...prev, [p]: data.url }))
      } catch { /* fallback to stream */ }
    }
  }

  return (
    <article className="song-card">
      <h3><a href={`#/song/${s.id}`}>{s.title || t('noTitle')}</a></h3>
      {s.owner_name && <p className="hint">{t('byAuthor')} {s.owner_name}</p>}
      <p className="hint">
        {s.avg_rating ? `${s.avg_rating}/5` : t('noRating')} ({s.rating_count})
      </p>
      <button className="ghost" style={{ fontSize: '0.75rem', marginTop: '0.5rem' }} onClick={loadPublicUrls}>
        {expanded ? t('hidePlayer') : <>{Icons.headphones} {t('listen')}</>}
      </button>
      {expanded && (
        <div style={{ marginTop: '0.5rem' }}>
          {['original', 'vocals', 'background'].map(purpose => (
            <div key={purpose} className="stem-row">
              <span className={`badge ${purpose === 'vocals' ? 'vocal' : purpose === 'background' ? 'inst' : 'neutral'}`} style={{ fontSize: '0.7rem', minWidth: '3rem', textAlign: 'center' }}>{t(purpose)}</span>
              <audio controls src={urls[purpose] || `/public/songs/${s.id}/stream/${purpose}`} style={{ flex: 1, height: 32 }} />
              <a href={urls[purpose] || `/public/songs/${s.id}/stream/${purpose}`} download={`${s.title || 'track'}_${purpose}.wav`} className="ghost" style={{ fontSize: '0.75rem' }}>{Icons.download}</a>
            </div>
          ))}
        </div>
      )}
      {user && (
        <div className="rating-bar" style={{ marginTop: '0.5rem' }}>
          {[1,2,3,4,5].map(n => (
            <button key={n} className="rating-btn" onClick={() => onRate(s.id, n)}>{n}</button>
          ))}
        </div>
      )}
    </article>
  )
}
