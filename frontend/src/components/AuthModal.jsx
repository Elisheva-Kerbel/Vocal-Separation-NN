import { useState, useEffect, useRef } from 'react'
import { Icons } from '../helpers.jsx'
import { MIN_PASSWORD_LENGTH } from '../api/auth.js'

function _getGoogleClientId() {
  const raw = document.querySelector('meta[name="google-client-id"]')?.content || ''
  if (!raw || raw.startsWith('%') || raw.length < 10) return null
  return raw
}

export default function AuthModal({ newAccount, setNewAccount, authError, setAuthError, authBusy, onSubmit, onGoogleAuth, onClose, t }) {
  const [showPw, setShowPw] = useState(false)
  const [googleReady, setGoogleReady] = useState(false)
  const googleBtnRef = useRef(null)
  const clientId = _getGoogleClientId()

  useEffect(() => {
    if (!clientId) return
    if (window.google?.accounts?.id && googleBtnRef.current) {
      window.google.accounts.id.renderButton(googleBtnRef.current, {
        type: 'standard', theme: 'outline', size: 'large', text: 'continue_with', locale: 'he', width: '100%',
      })
      setGoogleReady(true)
      return
    }
    const existing = document.querySelector('script[src*="accounts.google.com/gsi/client"]')
    if (existing) return
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.onload = () => {
      if (!window.google?.accounts?.id) return
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (resp) => onGoogleAuth(resp.credential),
      })
      if (googleBtnRef.current) {
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          type: 'standard', theme: 'outline', size: 'large', text: 'continue_with', locale: 'he', width: '100%',
        })
        setGoogleReady(true)
      }
    }
    document.head.appendChild(script)
  }, [clientId, onGoogleAuth])

  return (
    <div className="modal" onClick={onClose}>
      <form className="auth" role="dialog" aria-modal="true"
        aria-label={newAccount ? t('authTitleNew') : t('authTitle')}
        onClick={e => e.stopPropagation()} onSubmit={onSubmit}>
        <h2>{newAccount ? t('authTitleNew') : t('authTitle')}</h2>
        {authError && <p className="error" role="alert">{authError}</p>}

        {clientId && <div ref={googleBtnRef} style={{ display: 'flex', justifyContent: 'center', marginBottom: '0.75rem' }} />}

        {clientId && googleReady && <div className="auth-divider"><span>{t('or')}</span></div>}

        <label className="field"><span>{t('emailLabel')}</span><input name="email" type="email" autoComplete="username" required /></label>
        <label className="field"><span>{t('passwordLabel')}</span>
          <div className="password-field">
            <input name="password" type={showPw ? 'text' : 'password'}
              autoComplete={newAccount ? 'new-password' : 'current-password'} minLength={MIN_PASSWORD_LENGTH} required />
            <button type="button" className="password-toggle" onClick={() => setShowPw(!showPw)}
              aria-label={showPw ? 'hide' : 'show'}>{showPw ? Icons.eyeOff : Icons.eye}</button>
          </div>
        </label>
        <button className="btn full" type="submit" disabled={authBusy}>{authBusy ? '...' : newAccount ? t('signUp') : t('signIn')}</button>
        <p className="hint" style={{ textAlign: 'center' }}>
          {newAccount ? t('hasAccount') + ' ' : t('noAccount') + ' '}
          <button className="link" type="button" onClick={() => { setNewAccount(!newAccount); setAuthError('') }}>
            {newAccount ? t('signIn') : t('signUp')}
          </button>
        </p>
      </form>
    </div>
  )
}
