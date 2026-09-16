import { useState, useEffect } from 'react'
import { Icons } from '../helpers.jsx'
import { MIN_PASSWORD_LENGTH } from '../api/auth.js'
import { getSettings, updateSettings, changePassword, toggleTier, deleteAccount } from '../api/songs.js'

export default function SettingsPage({ user, setUser, onSignOut, t, lang, setLang }) {
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState(false)
  const [pwBusy, setPwBusy] = useState(false)
  const [showCurPw, setShowCurPw] = useState(false)
  const [showNewPw, setShowNewPw] = useState(false)

  useEffect(() => {
    getSettings().then(s => { setSettings(s); setLoading(false) }).catch(f => { setError(f.message); setLoading(false) })
  }, [])

  async function onUpdate(field, value) {
    try {
      const updated = await updateSettings({ [field]: value })
      setSettings(updated)
      setMsg('ההגדרות נשמרו.')
      setTimeout(() => setMsg(''), 2000)
    } catch (f) { setError(f.message) }
  }

  async function onToggleTier() {
    try {
      const res = await toggleTier()
      setSettings(prev => ({ ...prev, tier: res.tier }))
      setUser(prev => ({ ...prev, tier: res.tier }))
      setMsg(`הרמה שונתה ל${res.tier === 'pro' ? 'מקצועי' : 'בסיסי'}`)
      setTimeout(() => setMsg(''), 3000)
    } catch (f) { setError(f.message) }
  }

  async function onChangePassword(e) {
    e.preventDefault()
    const form = e.target
    const cur = form.curPw.value
    const nw = form.newPw.value
    setPwBusy(true)
    setError('')
    try {
      const res = await changePassword(cur, nw)
      setMsg(res.message)
      form.reset()
      setShowCurPw(false)
      setShowNewPw(false)
      setTimeout(() => setMsg(''), 3000)
    } catch (f) { setError(f.message) }
    setPwBusy(false)
  }

  async function onDeleteAccount() {
    try {
      await deleteAccount()
      setUser(null)
      window.location.hash = '#/'
    } catch (f) { setError(f.message) }
  }

  const ROLE_LABELS = { free: 'משתמש', user: 'משתמש', content_moderator: 'מנהל תוכן', user_admin: 'מנהל משתמשים', coupon_admin: 'מנהל קופונים', super_admin: 'מנהל ראשי' }

  if (loading) return <section className="page-section"><div className="wrap"><span className="spinner" /></div></section>

  return (
    <section className="page-section">
      <div className="wrap" style={{ maxWidth: '36rem' }}>
        <h2>{t('settingsTitle')}</h2>
        {error && <p className="error">{error}</p>}
        {msg && <p style={{ color: 'var(--ok)', fontWeight: 600 }}>{msg}</p>}

        {settings && (
          <>
            <div className="card" style={{ marginBottom: '1rem' }}>
              <p style={{ margin: '0 0 0.35rem' }}><b>{t('email')}:</b> {settings.email}</p>
              <p style={{ margin: '0 0 0.35rem' }}><b>{t('tier')}:</b> <span className={`badge ${settings.tier === 'pro' ? 'inst' : 'primary'}`}>{t(settings.tier)}</span></p>
              <p style={{ margin: 0 }}><b>{lang === 'en' ? 'Role' : 'תפקיד'}:</b> {ROLE_LABELS[settings.role] || settings.role}</p>
              {settings.role === 'super_admin' && (
                <div style={{ marginTop: '1rem', padding: '0.85rem', background: 'var(--raised)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <p style={{ margin: 0, fontWeight: 600, fontSize: '0.875rem' }}>החלפת רמה (מנהל)</p>
                      <p className="hint" style={{ margin: '0.15rem 0 0', fontSize: '0.8125rem' }}>
                        {settings.tier === 'pro' ? 'מודל: Demucs htdemucs_ft (Meta)' : 'מודל: בסיסי (STFT masking)'}
                      </p>
                    </div>
                    <button className="ghost" onClick={onToggleTier} style={{ whiteSpace: 'nowrap' }}>
                      עבור ל{settings.tier === 'pro' ? 'בסיסי' : 'מקצועי'}
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div className="card" style={{ marginBottom: '1rem' }}>
              <label className="field">
                <span>{t('prefLang')}</span>
                <select value={lang} onChange={e => { const v = e.target.value; setLang(v); onUpdate('preferred_language', v) }}>
                  <option value="he">עברית</option>
                  <option value="en">English</option>
                </select>
              </label>

              <div style={{ marginBottom: '1rem', padding: '0.75rem', background: 'var(--raised)', borderRadius: 'var(--radius-sm)' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input type="checkbox" checked={settings.email_opt_in} onChange={e => onUpdate('email_opt_in', e.target.checked)} />
                  <span style={{ fontWeight: 600, fontSize: '0.9375rem' }}>{t('emailOptIn')}</span>
                </label>
                <p className="hint" style={{ margin: '0.35rem 0 0', fontSize: '0.8125rem' }}>
                  {t('emailOptInDesc')}
                </p>
              </div>

            </div>

            <form className="card" style={{ marginBottom: '1rem' }} onSubmit={onChangePassword}>
              <h3 style={{ marginTop: 0 }}>{t('changePw')}</h3>
              <label className="field"><span>{t('currentPw')}</span>
                <div className="password-field">
                  <input name="curPw" type={showCurPw ? 'text' : 'password'} autoComplete="current-password" required minLength={MIN_PASSWORD_LENGTH} />
                  <button type="button" className="password-toggle" onClick={() => setShowCurPw(!showCurPw)}
                    aria-label={showCurPw ? 'הסתר' : 'הצג'}>{showCurPw ? Icons.eyeOff : Icons.eye}</button>
                </div>
              </label>
              <label className="field"><span>{t('newPw')}</span>
                <div className="password-field">
                  <input name="newPw" type={showNewPw ? 'text' : 'password'} autoComplete="new-password" required minLength={MIN_PASSWORD_LENGTH} />
                  <button type="button" className="password-toggle" onClick={() => setShowNewPw(!showNewPw)}
                    aria-label={showNewPw ? 'הסתר' : 'הצג'}>{showNewPw ? Icons.eyeOff : Icons.eye}</button>
                </div>
              </label>
              <button className="btn" type="submit" disabled={pwBusy}>{pwBusy ? '...' : t('updatePw')}</button>
            </form>

            <div className="card danger-zone">
              <h3 style={{ marginTop: 0 }}>{t('dangerZone')}</h3>
              {!deleteConfirm ? (
                <button className="btn danger" onClick={() => setDeleteConfirm(true)}>{t('deleteAccountBtn')}</button>
              ) : (
                <>
                  <p style={{ color: 'var(--danger)', fontSize: '0.9375rem' }}>פעולה זו תמחק את החשבון שלך, כל השירים וכל הנתונים. לא ניתן לבטל.</p>
                  <div className="row">
                    <button className="btn danger" onClick={onDeleteAccount}>כן, מחק</button>
                    <button className="btn secondary" onClick={() => setDeleteConfirm(false)}>ביטול</button>
                  </div>
                </>
              )}
            </div>
          </>
        )}
      </div>
    </section>
  )
}
