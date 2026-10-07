import { useState, useEffect, useRef } from 'react'
import { statusBadgeClass, Icons } from '../helpers.jsx'
import { getSong, getListenUrl, getDownloadUrl, renameSong, deleteSong } from '../api/songs.js'

export default function SongPage({ songId, t }) {
  const [song, setSong] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [listenUrls, setListenUrls] = useState({})
  const [active, setActive] = useState('original')
  const [loaded, setLoaded] = useState({ original: true })
  const [editingTitle, setEditingTitle] = useState(false)
  const [titleDraft, setTitleDraft] = useState('')
  const [msg, setMsg] = useState('')
  const [elapsed, setElapsed] = useState(0)
  const players = useRef({})

  const isProcessing = song && (song.status === 'processing' || song.status === 'uploaded' || song.status === 'queued')

  useEffect(() => {
    let live = true
    let timer = null
    loadSong()
    async function loadSong() {
      try {
        const s = await getSong(songId)
        if (live) { setSong(s); setLoading(false); setTitleDraft(s.title || '') }
        if (s.status === 'processing' || s.status === 'uploaded' || s.status === 'queued') {
          timer = setTimeout(loadSong, 3000)
        }
        if (s.status === 'ready' && live) {
          const urls = {}
          for (const p of ['original', 'vocals', 'background']) {
            const hasStem = s.stems && s.stems.some(st => st.purpose === p)
            if (hasStem) {
              try {
                const r = await getListenUrl(songId, p)
                urls[p] = r.url
              } catch { urls[p] = `/songs/${songId}/stream/${p}` }
            }
          }
          if (live) setListenUrls(urls)
        }
      } catch (f) { if (live) { setError(f.message); setLoading(false) } }
    }
    return () => { live = false; if (timer) clearTimeout(timer) }
  }, [songId])

  useEffect(() => {
    if (!isProcessing) return undefined
    setElapsed(0)
    const tick = setInterval(() => setElapsed(s => s + 1), 1000)
    return () => clearInterval(tick)
  }, [isProcessing])

  function switchTo(id) {
    setLoaded(prev => ({ ...prev, [id]: true }))
    const from = players.current[active]
    const to = players.current[id]
    if (from && to && to.readyState >= 1) {
      to.currentTime = from.currentTime
      if (!from.paused) { from.pause(); to.play() }
    } else if (from && !from.paused) {
      from.pause()
    }
    setActive(id)
  }

  async function onDownload(purpose) {
    try {
      const r = await getDownloadUrl(songId, purpose)
      window.location.href = r.url
    } catch {
      const a = document.createElement('a')
      a.href = `/songs/${songId}/stream/${purpose}`
      a.download = `${song.title || 'track'}_${purpose}.wav`
      a.click()
    }
  }

  async function onRename() {
    if (!titleDraft.trim()) return
    try {
      await renameSong(songId, titleDraft.trim())
      setSong(prev => ({ ...prev, title: titleDraft.trim() }))
      setEditingTitle(false)
      setMsg(t('titleUpdated'))
      setTimeout(() => setMsg(''), 2000)
    } catch (f) { setError(f.message) }
  }

  async function onDelete() {
    try {
      await deleteSong(songId)
      window.location.hash = '#/upload'
    } catch (f) { setError(f.message) }
  }

  if (loading) return <section className="page-section"><div className="wrap"><span className="spinner" /></div></section>
  if (error && !song) return <section className="page-section"><div className="wrap"><p className="error">{error}</p></div></section>
  if (!song) return null

  const STEM_ORDER = ['original', 'vocals', 'background']
  const STEM_CSS = { original: '', vocals: 'vocal', background: 'inst' }
  const STEM_NAMES = { original: t('original'), vocals: t('vocals'), background: t('background') }
  const mm = String(Math.floor(elapsed / 60)).padStart(2, '0')
  const ss = String(elapsed % 60).padStart(2, '0')

  return (
    <section className="page-section">
      <div className="wrap" style={{ maxWidth: '48rem' }}>
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          {!isProcessing && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              {editingTitle ? (
                <div style={{ display: 'flex', gap: '0.5rem', flex: 1 }}>
                  <input className="field-input" value={titleDraft} onChange={e => setTitleDraft(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') onRename(); if (e.key === 'Escape') setEditingTitle(false) }}
                    style={{ flex: 1, fontSize: '1.1rem' }} autoFocus />
                  <button className="btn" onClick={onRename} style={{ padding: '0.4rem 1rem' }}>{t('save')}</button>
                  <button className="ghost" onClick={() => { setEditingTitle(false); setTitleDraft(song.title || '') }}>{t('cancel')}</button>
                </div>
              ) : (
                <h2 style={{ margin: 0, cursor: 'pointer' }} onClick={() => setEditingTitle(true)} title={t('clickToRename')}>
                  {song.title || t('noTitle')} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>&#9998;</span>
                </h2>
              )}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <span className={statusBadgeClass(song.status)}>{t(song.status)}</span>
                <span className="badge neutral">{t(song.visibility)}</span>
              </div>
            </div>
          )}

          {msg && <p style={{ color: 'var(--ok)', fontWeight: 600, margin: '0 0 1rem' }}>{msg}</p>}
          {error && <p className="error">{error}</p>}

          {isProcessing && (
            <div style={{ textAlign: 'center', padding: '2rem 0' }}>
              <span className="spinner" style={{ width: 48, height: 48 }} />
              <h3 style={{ margin: '1.5rem 0 0.5rem', color: 'var(--text)' }}>{t('separating')}</h3>
              <p className="hint">{t('waitNote')}</p>
              <p style={{ fontFamily: 'monospace', fontSize: '1.5rem', color: 'var(--primary)', margin: '1rem 0 0' }}>{mm}:{ss}</p>
            </div>
          )}

          {song.status === 'ready' && (
            <div style={{ marginTop: '0.5rem' }}>
              <div className="segmented" role="tablist" aria-label="בחר ערוץ">
                {STEM_ORDER.map(id => (
                  <button key={id} role="tab" type="button"
                    aria-selected={active === id}
                    className={`seg${active === id ? ' on' : ''}${active === id && STEM_CSS[id] ? ` ${STEM_CSS[id]}` : ''}`}
                    onClick={() => switchTo(id)}>
                    {STEM_NAMES[id]}
                  </button>
                ))}
              </div>

              {STEM_ORDER.map(id => (
                <audio key={id} ref={node => { players.current[id] = node }}
                  controls={active === id} src={loaded[id] ? (listenUrls[id] || '') : ''}
                  preload={active === id ? 'auto' : 'none'}
                  style={{ width: '100%', display: active === id ? 'block' : 'none', marginTop: '1rem' }} />
              ))}

              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                {STEM_ORDER.map(id => (
                  <button key={id} className="ghost" onClick={() => onDownload(id)} style={{ fontSize: '0.85rem' }}>
                    {Icons.download} {STEM_NAMES[id]}
                  </button>
                ))}
              </div>
            </div>
          )}

          {song.status === 'failed' && song.job && (
            <p className="error">{song.job.error_message || t('separationFailed')}</p>
          )}
        </div>

        {song.status === 'ready' && (
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <a href="#/library" className="btn secondary">{t('toLibrary')}</a>
            <button className="btn danger" onClick={onDelete}>{t('delete')}</button>
          </div>
        )}
        {song.status === 'failed' && (
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <a href="#/upload" className="btn">{t('uploadNew')}</a>
            <button className="btn danger" onClick={onDelete}>{t('delete')}</button>
          </div>
        )}
      </div>
    </section>
  )
}
