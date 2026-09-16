import { useState, useEffect } from 'react'
import { getAdminStats, getAdminUsers, getAdminSongs, blockUser, unblockUser } from '../api/songs.js'

const STATUS_COLORS = { ready: '#22c55e', processing: '#f59e0b', queued: '#3b82f6', uploaded: '#3b82f6', failed: '#ef4444' }

export default function AdminPage({ user }) {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [songs, setSongs] = useState([])
  const [tab, setTab] = useState('dashboard')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => { loadData() }, [])

  async function loadData() {
    try {
      const [s, u, sg] = await Promise.all([getAdminStats(), getAdminUsers(0, 100), getAdminSongs(0, 100)])
      setStats(s); setUsers(u); setSongs(sg); setLoading(false)
    } catch (e) { setError(e.message); setLoading(false) }
  }

  async function handleBlock(userId, blocked) {
    try {
      if (blocked) await unblockUser(userId); else await blockUser(userId)
      const u = await getAdminUsers(0, 100)
      setUsers(u)
    } catch (e) { setError(e.message) }
  }

  if (loading) return <section className="page-section"><div className="wrap"><span className="spinner" /></div></section>

  return (
    <section className="page-section">
      <div className="wrap">
        <h2>לוח ניהול</h2>
        {error && <p className="error">{error}</p>}

        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
          {['dashboard', 'users', 'songs'].map(t => (
            <button key={t} className={tab === t ? 'btn' : 'ghost'} onClick={() => setTab(t)}>
              {t === 'dashboard' ? 'סטטיסטיקות' : t === 'users' ? 'משתמשים' : 'שירים'}
            </button>
          ))}
        </div>

        {tab === 'dashboard' && stats && (
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem' }}>
            {[
              ['משתמשים', stats.total_users, '#7c3aed'],
              ['פעילים', stats.active_users, '#22c55e'],
              ['שירים', stats.total_songs, '#3b82f6'],
              ['ציבוריים', stats.public_songs, '#f59e0b'],
              ['מוכנים', stats.ready_songs, '#22c55e'],
              ['בעיבוד', stats.processing_songs, '#f59e0b'],
              ['נכשלו', stats.failed_songs, '#ef4444'],
            ].map(([label, val, color]) => (
              <div key={label} className="card" style={{ textAlign: 'center', padding: '1.25rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 700, color }}>{val}</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{label}</div>
              </div>
            ))}
          </div>
        )}

        {tab === 'users' && (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border)' }}>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>מייל</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>סטטוס</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>תפקיד</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>רמה</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>תאריך</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>פעולות</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '0.5rem' }}>{u.email}</td>
                    <td style={{ padding: '0.5rem' }}>
                      <span className={`badge ${u.status === 'active' ? 'primary' : 'danger'}`}>{u.status === 'active' ? 'פעיל' : 'חסום'}</span>
                    </td>
                    <td style={{ padding: '0.5rem' }}>{u.role === 'super_admin' ? 'מנהל' : 'משתמש'}</td>
                    <td style={{ padding: '0.5rem' }}>{u.tier === 'pro' ? 'מקצועי' : 'בסיסי'}</td>
                    <td style={{ padding: '0.5rem' }}>{new Date(u.created_at).toLocaleDateString('he-IL')}</td>
                    <td style={{ padding: '0.5rem' }}>
                      {u.email !== user.email && (
                        <button className="ghost" style={{ fontSize: '0.75rem', color: u.status === 'active' ? 'var(--danger)' : '#22c55e' }}
                          onClick={() => handleBlock(u.id, u.status === 'blocked')}>
                          {u.status === 'active' ? 'חסום' : 'שחרר'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'songs' && (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border)' }}>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>שם</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>בעלים</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>סטטוס</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>נראות</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>מודל</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>תאריך</th>
                </tr>
              </thead>
              <tbody>
                {songs.map(s => (
                  <tr key={s.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '0.5rem' }}><a href={`#/song/${s.id}`}>{s.title || 'ללא שם'}</a></td>
                    <td style={{ padding: '0.5rem' }}>{s.owner_email ? s.owner_email.split('@')[0] : '-'}</td>
                    <td style={{ padding: '0.5rem' }}>
                      <span style={{ color: STATUS_COLORS[s.status] || 'inherit' }}>{s.status === 'ready' ? 'מוכן' : s.status === 'failed' ? 'נכשל' : s.status === 'processing' ? 'בעיבוד' : s.status}</span>
                    </td>
                    <td style={{ padding: '0.5rem' }}>{s.visibility === 'public' ? 'ציבורי' : 'פרטי'}</td>
                    <td style={{ padding: '0.5rem' }}>{s.model_tier === 'professional' ? 'מקצועי' : 'בסיסי'}</td>
                    <td style={{ padding: '0.5rem' }}>{new Date(s.created_at).toLocaleDateString('he-IL')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}
