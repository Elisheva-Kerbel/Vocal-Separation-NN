import { useEffect, useState } from 'react'

import { currentUser, googleLogin, signIn, signOut, signUp } from './api/auth.js'
import { getQuota } from './api/songs.js'

import { useLang } from './i18n.js'
import { Icons, useHash } from './helpers.jsx'

import AuthModal from './components/AuthModal.jsx'
import NeedAuth from './components/NeedAuth.jsx'

import HomePage from './pages/HomePage.jsx'
import UploadPage from './pages/UploadPage.jsx'
import SongPage from './pages/SongPage.jsx'
import LibraryPage from './pages/LibraryPage.jsx'
import ExplorePage from './pages/ExplorePage.jsx'
import UpgradePage from './pages/UpgradePage.jsx'
import AdminPage from './pages/AdminPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'

export default function App() {
  const [user, setUser] = useState(null)
  const [authOpen, setAuthOpen] = useState(false)
  const [newAccount, setNewAccount] = useState(false)
  const [authError, setAuthError] = useState('')
  const [authBusy, setAuthBusy] = useState(false)
  const [quota, setQuota] = useState(null)
  const hash = useHash()
  const { lang, setLang, t } = useLang(user)

  function refreshQuota() {
    getQuota().then(setQuota).catch(() => {})
  }

  useEffect(() => {
    let live = true
    currentUser().then((account) => { if (live) { setUser(account); if (account) refreshQuota() } })
    return () => { live = false }
  }, [])

  useEffect(() => {
    if (!authOpen) return undefined
    const onKey = (e) => { if (e.key === 'Escape') setAuthOpen(false) }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [authOpen])

  function openAuth(creating) {
    setNewAccount(creating)
    setAuthError('')
    setAuthOpen(true)
  }

  async function onAuthSubmit(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setAuthBusy(true)
    setAuthError('')
    try {
      const submit = newAccount ? signUp : signIn
      setUser(await submit(form.get('email'), form.get('password')))
      setAuthOpen(false)
    } catch (failure) {
      setAuthError(failure.message)
    } finally {
      setAuthBusy(false)
    }
  }

  async function onGoogleAuth(credential) {
    setAuthBusy(true)
    setAuthError('')
    try {
      setUser(await googleLogin(credential))
      setAuthOpen(false)
    } catch (failure) {
      setAuthError(failure.message)
    } finally {
      setAuthBusy(false)
    }
  }

  async function onSignOut() {
    await signOut().catch(() => {})
    setUser(null)
    window.location.hash = '#/'
  }

  const currentPage = hash.startsWith('#/song/') ? 'song'
    : hash === '#/library' ? 'library'
    : hash === '#/explore' ? 'explore'
    : hash === '#/settings' ? 'settings'
    : hash === '#/upload' ? 'upload'
    : hash === '#/upgrade' ? 'upgrade'
    : hash === '#/admin' ? 'admin'
    : 'home'

  let page
  if (hash.startsWith('#/song/')) {
    page = <SongPage songId={hash.replace('#/song/', '')} user={user} t={t} />
  } else if (hash === '#/library') {
    page = user ? <LibraryPage user={user} t={t} /> : <NeedAuth openAuth={openAuth} t={t} />
  } else if (hash === '#/explore') {
    page = <ExplorePage user={user} t={t} />
  } else if (hash === '#/settings') {
    page = user ? <SettingsPage user={user} setUser={setUser} onSignOut={onSignOut} t={t} lang={lang} setLang={setLang} /> : <NeedAuth openAuth={openAuth} t={t} />
  } else if (hash === '#/upload') {
    page = user ? <UploadPage user={user} quota={quota} onUploaded={refreshQuota} t={t} /> : <NeedAuth openAuth={openAuth} t={t} />
  } else if (hash === '#/upgrade') {
    page = user ? <UpgradePage user={user} setUser={setUser} t={t} /> : <NeedAuth openAuth={openAuth} t={t} />
  } else if (hash === '#/admin') {
    page = user && user.role === 'super_admin' ? <AdminPage user={user} t={t} /> : <NeedAuth openAuth={openAuth} t={t} />
  } else {
    page = <HomePage user={user} openAuth={openAuth} t={t} />
  }

  return (
    <div className={`app-layout ${user ? '' : 'no-sidebar'}`}>
      {user && (
        <aside className="sidebar">
          <a href="#/" className="sidebar-brand">
            <span className="sidebar-brand-icon">{Icons.headphones}</span>
            <span className="sidebar-brand-name">VocalSplit</span>
          </a>
          <nav className="sidebar-nav">
            <a href="#/" className={`sidebar-link ${currentPage === 'home' ? 'active' : ''}`}>{Icons.home}<span>{t('home')}</span></a>
            <a href="#/upload" className={`sidebar-link ${currentPage === 'upload' ? 'active' : ''}`}>{Icons.upload}<span>{t('upload')}</span></a>
            <a href="#/library" className={`sidebar-link ${currentPage === 'library' ? 'active' : ''}`}>{Icons.library}<span>{t('myLibrary')}</span></a>
            <a href="#/explore" className={`sidebar-link ${currentPage === 'explore' ? 'active' : ''}`}>{Icons.explore}<span>{t('explore')}</span></a>
            <a href="#/settings" className={`sidebar-link ${currentPage === 'settings' ? 'active' : ''}`}>{Icons.settings}<span>{t('settings')}</span></a>
            {user.role === 'super_admin' && (
              <a href="#/admin" className={`sidebar-link ${currentPage === 'admin' ? 'active' : ''}`}>{Icons.shield}<span>{t('admin')}</span></a>
            )}
          </nav>
          {user.tier !== 'pro' && (
            <a href="#/upgrade" className="sidebar-upgrade-btn">{t('upgrade')} →</a>
          )}
          <div className="sidebar-spacer" />
          <div className="sidebar-user">
            <div className="sidebar-user-email">{user.email}</div>
            <div className="sidebar-user-tier">{t(user.tier)}</div>
            {quota && (
              <div className="sidebar-quota">
                {user.tier === 'pro' ? (
                  <>
                    <span className="quota-line">{t('proQuota')}: {quota.professional_used}/{quota.professional_limit}</span>
                    <span className="quota-line">{t('basicQuota')}: {t('unlimited')}</span>
                  </>
                ) : (
                  <span className="quota-line">{t('basicQuota')}: {quota.basic_used}/{quota.basic_limit}</span>
                )}
              </div>
            )}
            <div className="sidebar-user-actions">
              <button className="ghost" style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }} onClick={onSignOut}>{Icons.logout} {t('signOut')}</button>
            </div>
          </div>
        </aside>
      )}

      <header className="topbar">
        <div className="topbar-inner">
          <a href="#/" className="brand">VocalSplit</a>
          <nav className="nav">
            <a href="#/">{t('home')}</a>
            <a href="#/explore">{t('explore')}</a>
            <button className="topbar-signin" type="button" onClick={() => openAuth(false)}>{t('signIn')}</button>
          </nav>
        </div>
      </header>

      {user && (
        <nav className="mobile-nav">
          <a href="#/" className={currentPage === 'home' ? 'active' : ''}>{Icons.home}<span>{t('home')}</span></a>
          <a href="#/upload" className={currentPage === 'upload' ? 'active' : ''}>{Icons.upload}<span>{t('uploadShort')}</span></a>
          <a href="#/library" className={currentPage === 'library' ? 'active' : ''}>{Icons.library}<span>{t('libraryShort')}</span></a>
          <a href="#/explore" className={currentPage === 'explore' ? 'active' : ''}>{Icons.explore}<span>{t('explore')}</span></a>
          <a href="#/settings" className={currentPage === 'settings' ? 'active' : ''}>{Icons.settings}<span>{t('settings')}</span></a>
        </nav>
      )}

      <div className="content-area">
        <main>{page}</main>
        <footer><div className="wrap">{t('footer')}</div></footer>
      </div>

      {authOpen && <AuthModal
        newAccount={newAccount} setNewAccount={setNewAccount}
        authError={authError} setAuthError={setAuthError}
        authBusy={authBusy} onSubmit={onAuthSubmit}
        onGoogleAuth={onGoogleAuth}
        onClose={() => setAuthOpen(false)}
        t={t}
      />}
    </div>
  )
}
