import { useState, useEffect } from 'react'
import { Icons } from '../helpers.jsx'
import { getLibrary, deleteSong, publishSong, unpublishSong } from '../api/songs.js'
import LibrarySongCard from '../components/LibrarySongCard.jsx'

export default function LibraryPage({ user, t }) {
  const [songs, setSongs] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => { loadLibrary() }, [])

  async function loadLibrary() {
    try {
      const res = await getLibrary()
      setSongs(res.songs); setTotal(res.total); setLoading(false)
    } catch (f) { setError(f.message); setLoading(false) }
  }

  async function onDelete(songId) {
    try { await deleteSong(songId); loadLibrary() }
    catch (f) { setError(f.message) }
  }

  async function onPublish(songId) {
    try { await publishSong(songId); loadLibrary() }
    catch (f) { setError(f.message) }
  }

  async function onUnpublish(songId) {
    try { await unpublishSong(songId); loadLibrary() }
    catch (f) { setError(f.message) }
  }

  return (
    <section className="page-section">
      <div className="wrap">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0 }}>{t('myLibrary')} ({total})</h2>
          <a href="#/upload" className="btn" style={{ margin: 0 }}>{Icons.upload} {t('upload')}</a>
        </div>

        {error && <p className="error">{error}</p>}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem 0' }}><span className="spinner" /></div>
        ) : songs.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>{t('libEmpty')}</p>
            <a href="#/upload" className="btn" style={{ maxWidth: '16rem', margin: '0 auto' }}>{t('uploadFirst')}</a>
          </div>
        ) : (
          <div className="grid">
            {songs.map(s => (
              <LibrarySongCard key={s.id} song={s} onPublish={onPublish} onUnpublish={onUnpublish} onDelete={onDelete} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
