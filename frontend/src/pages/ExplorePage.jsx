import { useState, useEffect } from 'react'
import { getPublicLibrary, rateSong } from '../api/songs.js'
import PublicSongCard from '../components/PublicSongCard.jsx'

export default function ExplorePage({ user, t }) {
  const [songs, setSongs] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getPublicLibrary().then(res => { setSongs(res.songs); setTotal(res.total); setLoading(false) })
      .catch(f => { setError(f.message); setLoading(false) })
  }, [])

  async function onRate(songId, score) {
    try { await rateSong(songId, score) } catch (f) { setError(f.message) }
  }

  return (
    <section className="page-section">
      <div className="wrap">
        <h2>{t('exploreTitle')} ({total})</h2>
        {error && <p className="error">{error}</p>}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem 0' }}><span className="spinner" /></div>
        ) : songs.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
            <p style={{ color: 'var(--text-muted)' }}>{t('exploreEmpty')}</p>
          </div>
        ) : (
          <div className="grid">
            {songs.map(s => (
              <PublicSongCard key={s.id} song={s} user={user} onRate={onRate} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
