import { useState } from 'react'
import { subscribe } from '../api/songs.js'

export default function UpgradePage({ user, setUser, t }) {
  const [selectedPlan, setSelectedPlan] = useState('monthly')
  const [couponCode, setCouponCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  if (user.tier === 'pro') {
    return (
      <section className="page-section">
        <div className="wrap upgrade-page" style={{ textAlign: 'center', padding: '3rem 0' }}>
          <h2>{t('upgradeTitle')}</h2>
          <p className="hint" style={{ marginBottom: '1.5rem' }}>{t('upgradeSub')}</p>
          <a href="#/upload" className="btn">{t('uploadSong')}</a>
        </div>
      </section>
    )
  }

  async function onSubscribe() {
    setBusy(true); setError(''); setMsg('')
    try {
      const res = await subscribe(selectedPlan, couponCode || undefined)
      setMsg(res.message)
      setUser(prev => ({ ...prev, tier: 'pro' }))
    } catch (f) { setError(f.message) }
    finally { setBusy(false) }
  }

  return (
    <section className="page-section">
      <div className="wrap upgrade-page">
        <h2>{t('upgradeTitle')}</h2>
        <p className="lede" style={{ margin: '0.5rem 0 2rem' }}>{t('upgradeSub')}</p>

        {msg && <div className="card" style={{ textAlign: 'center', marginBottom: '1.5rem', borderColor: 'var(--ok)' }}>
          <p style={{ color: 'var(--ok)', fontWeight: 600, margin: 0 }}>{msg}</p>
          <a href="#/upload" className="btn" style={{ marginTop: '1rem' }}>העלה שיר עכשיו</a>
        </div>}

        {!msg && (
          <>
            <div className="grid two" style={{ marginBottom: '2rem' }}>
              <article className="tier">
                <div className="tier-head"><h3>בסיסי</h3><span className="badge primary">הרמה שלך</span></div>
                <div className="tier-price"><span className="price-amount">₪0</span><span className="price-period">/ לתמיד</span></div>
                <ul><li>שירה + מוזיקה</li><li>3 הפרדות בסיסיות ביום</li><li>הורדה בפורמט WAV</li></ul>
              </article>
              <article className="tier pro live">
                <div className="tier-head"><h3>מקצועי</h3><span className="badge inst">Pro</span></div>
                <div className="tier-price"><span className="price-amount">₪29</span><span className="price-period">/ חודש</span></div>
                <ul>
                  <li>מודל Demucs (Meta) - איכות סטודיו</li>
                  <li>10 הפרדות מקצועיות + בסיסי ללא הגבלה</li>
                  <li>עדיפות בתור העיבוד</li>
                  <li>תמיכה מועדפת</li>
                </ul>
              </article>
            </div>

            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginTop: 0 }}>בחר תכנית</h3>
              <div className="plan-selector">
                <button className={`plan-option ${selectedPlan === 'monthly' ? 'selected' : ''}`}
                  onClick={() => setSelectedPlan('monthly')}>
                  <span className="plan-name">חודשי</span>
                  <span className="plan-price">₪29<small>/חודש</small></span>
                </button>
                <button className={`plan-option ${selectedPlan === 'annual' ? 'selected' : ''}`}
                  onClick={() => setSelectedPlan('annual')}>
                  <span className="plan-save">חסכון של ₪99!</span>
                  <span className="plan-name">שנתי</span>
                  <span className="plan-price">₪249<small>/שנה</small></span>
                  <span className="plan-monthly">₪20.75 לחודש</span>
                </button>
              </div>
            </div>

            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginTop: 0 }}>יש לך קופון?</h3>
              <div className="coupon-row">
                <input type="text" placeholder="הזן קוד קופון" value={couponCode}
                  onChange={e => setCouponCode(e.target.value)} />
              </div>
            </div>

            <div className="payment-placeholder">
              <p style={{ fontWeight: 600, margin: '0 0 0.5rem' }}>תשלום</p>
              <p style={{ margin: 0 }}>שער תשלום יתווסף בקרוב. כרגע ניתן לשדרג באמצעות קופון או לנסות את השירות.</p>
            </div>

            {error && <p className="error" style={{ marginTop: '1rem' }}>{error}</p>}

            <button className="btn pro-upgrade full" onClick={onSubscribe} disabled={busy} style={{ marginTop: '1.5rem' }}>
              {busy ? 'מעבד...' : couponCode ? 'הפעל קופון ושדרג' : selectedPlan === 'monthly' ? 'שדרג - ₪29/חודש' : 'שדרג - ₪249/שנה'}
            </button>

            <a href="#/" className="link" style={{ display: 'block', textAlign: 'center', marginTop: '1rem' }}>חזרה לדף הראשי</a>
          </>
        )}
      </div>
    </section>
  )
}
