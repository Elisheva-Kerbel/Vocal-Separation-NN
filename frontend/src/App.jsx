// StemSpace local demo page (FAST-DEMO-004) + local MVP accounts (P3-004).
//
// One page. The upload -> separate -> compare flow is REAL and runs against the
// local Basic model, and sign-up / sign-in are now REAL too (DEC-0010, approved for
// Local MVP) — the `Sign in` control is no longer inert. Everything else on the page
// is presentation, and anything not built yet is labelled `Planned` rather than
// mocked up as if it worked: no invented price, no fake library rows. That keeps the
// richer product framing honest about what exists (DEC-0009 §4 — no production
// claim, and Professional must never be shown as implemented).
//
// Accounts do not gate anything yet: the demo stays fully usable signed out, and
// there is no library, billing, admin or tier behaviour behind signing in.
//
// Plain React + CSS, no UI library, no new dependency (DEC-0009 D8). Every backend
// call goes through ./api/demo.js and ./api/auth.js (docs/coding-rules.md §2).
import { useEffect, useRef, useState } from 'react'

import { MIN_PASSWORD_LENGTH, currentUser, signIn, signOut, signUp } from './api/auth.js'
import { MAX_UPLOAD_BYTES, separate, validateFile } from './api/demo.js'

const STEM_LABELS = { vocals: 'Vocals', background: 'Background' }

const STEPS = [
  { n: '01', title: 'Drop a track', body: 'MP3 or WAV, up to 20 MB. It never leaves this machine.' },
  { n: '02', title: 'Separate', body: 'The Basic model splits the track into vocals and background.' },
  { n: '03', title: 'Compare & download', body: 'A/B the stems against the original, then save them.' },
]

const TIERS = [
  {
    name: 'Basic',
    state: 'Running in this demo',
    live: true,
    points: ['Vocals + background', 'Local processing', 'WAV download'],
  },
  {
    name: 'Professional',
    state: 'Planned',
    live: false,
    points: ['Not implemented', 'No pricing decided', 'Not part of this demo'],
  },
]

const ROADMAP = [
  { title: 'Cloud library', body: 'Your tracks and stems, kept privately across sessions.' },
  { title: 'Background processing', body: 'Queue long jobs instead of waiting on the request.' },
  { title: 'Per-account limits', body: 'Quotas, history and anything an account unlocks.' },
]

function formatBytes(bytes) {
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function formatClock(seconds) {
  const mm = String(Math.floor(seconds / 60)).padStart(2, '0')
  const ss = String(seconds % 60).padStart(2, '0')
  return `${mm}:${ss}`
}

export default function App() {
  const [user, setUser] = useState(null)
  const [authOpen, setAuthOpen] = useState(false)
  const [newAccount, setNewAccount] = useState(false)
  const [authError, setAuthError] = useState('')
  const [authBusy, setAuthBusy] = useState(false)
  const [file, setFile] = useState(null)
  const [sourceUrl, setSourceUrl] = useState('')
  const [stems, setStems] = useState(null)
  const [active, setActive] = useState('original')
  const [busy, setBusy] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState('')
  const players = useRef({})

  // One bootstrap call to establish session state. A 401 is not an error — the
  // client returns null for it, which simply means signed out.
  useEffect(() => {
    let live = true
    currentUser().then((account) => {
      if (live) setUser(account)
    })
    return () => {
      live = false
    }
  }, [])

  // Escape closes the account dialog, like any other modal.
  useEffect(() => {
    if (!authOpen) return undefined
    const onKey = (event) => {
      if (event.key === 'Escape') setAuthOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [authOpen])

  // Let the browser play the picked file straight from memory, so the result view
  // can A/B a stem against the original without a second round trip.
  useEffect(() => {
    if (!file) {
      setSourceUrl('')
      return undefined
    }
    const url = URL.createObjectURL(file)
    setSourceUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  // A real elapsed clock — the honest alternative to a fabricated percentage or ETA
  // (DEC-0009 §6 forbids fake progress).
  useEffect(() => {
    if (!busy) return undefined
    setElapsed(0)
    const tick = setInterval(() => setElapsed((seconds) => seconds + 1), 1000)
    return () => clearInterval(tick)
  }, [busy])

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

  async function onSignOut() {
    // The cookie is the session, so the backend clears it. Local state is cleared
    // either way — there is nothing stored here to fall out of sync.
    await signOut().catch(() => {})
    setUser(null)
  }

  function pick(candidate) {
    if (!candidate) return
    const problem = validateFile(candidate)
    setError(problem)
    setFile(problem ? null : candidate)
  }

  function onDrop(event) {
    event.preventDefault()
    setDragging(false)
    pick(event.dataTransfer.files[0])
  }

  async function onSeparate() {
    setBusy(true)
    setError('')
    try {
      setStems(await separate(file))
      setActive('original')
    } catch (failure) {
      setError(failure.message)
    } finally {
      setBusy(false)
    }
  }

  // Switching sources keeps the playhead, so the same moment can be heard on the
  // original and on each stem.
  function switchTo(id) {
    const from = players.current[active]
    const to = players.current[id]
    if (from && to) {
      to.currentTime = from.currentTime
      if (!from.paused) {
        from.pause()
        to.play()
      }
    }
    setActive(id)
  }

  function reset() {
    setFile(null)
    setStems(null)
    setActive('original')
    setError('')
  }

  const tracks = stems && [
    { id: 'original', label: 'Original', url: sourceUrl, download: '' },
    ...stems.map(({ stem, url }) => ({
      id: stem,
      label: STEM_LABELS[stem] ?? stem,
      url,
      download: `${stem}.wav`,
    })),
  ]

  return (
    <>
      <header className="topbar">
        <div className="wrap topbar-inner">
          <span className="brand">StemSpace</span>
          <nav className="nav">
            <a href="#how">How it works</a>
            <a href="#tiers">Tiers</a>
            {user ? (
              <>
                <span className="who">{user.email}</span>
                <button className="ghost" type="button" onClick={onSignOut}>
                  Sign out
                </button>
              </>
            ) : (
              <button className="ghost" type="button" onClick={() => openAuth(false)}>
                Sign in
              </button>
            )}
          </nav>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="wrap">
            <p className="pill">Basic · Local demo</p>
            <h1>
              Split any track into <em>vocals</em> and <em>background</em>.
            </h1>
            <p className="lede">
              Drop a song in, hear the two stems side by side with the original, and download them.
              Everything runs locally on this machine.
            </p>

            <div className="panel">
              {error && (
                <p className="error" role="alert">
                  {error}
                </p>
              )}

              {tracks ? (
                <div className="result">
                  <div className="segmented" role="tablist" aria-label="Choose a track">
                    {tracks.map(({ id, label }) => (
                      <button
                        key={id}
                        role="tab"
                        type="button"
                        aria-selected={active === id}
                        className={active === id ? 'seg on' : 'seg'}
                        onClick={() => switchTo(id)}
                      >
                        {label}
                      </button>
                    ))}
                  </div>

                  {tracks.map(({ id, url }) => (
                    <audio
                      key={id}
                      ref={(node) => {
                        players.current[id] = node
                      }}
                      className={active === id ? 'player' : 'player hidden'}
                      controls
                      src={url}
                    />
                  ))}

                  <p className="hint">Switching keeps your place, so you can A/B the same moment.</p>

                  <div className="row">
                    {tracks
                      .filter((track) => track.download)
                      .map(({ id, label, url, download }) => (
                        <a key={id} className="btn secondary" href={url} download={download}>
                          Download {label.toLowerCase()}
                        </a>
                      ))}
                  </div>
                  <button className="btn" type="button" onClick={reset}>
                    Separate another track
                  </button>
                </div>
              ) : busy ? (
                <div className="working">
                  <span className="spinner" aria-hidden="true" />
                  <div>
                    <p className="working-title" aria-live="polite">
                      Separating vocals and background…
                    </p>
                    <p className="hint">
                      This can take a couple of minutes. Elapsed <b>{formatClock(elapsed)}</b>.
                    </p>
                  </div>
                </div>
              ) : (
                <>
                  <label
                    className={dragging ? 'drop over' : 'drop'}
                    onDragOver={(event) => {
                      event.preventDefault()
                      setDragging(true)
                    }}
                    onDragLeave={() => setDragging(false)}
                    onDrop={onDrop}
                  >
                    <input
                      type="file"
                      accept="audio/mpeg,audio/wav,.mp3,.wav"
                      onChange={(event) => pick(event.target.files[0])}
                    />
                    <b>Drop a track here</b>
                    <span className="hint">
                      or click to browse · MP3 or WAV · up to {formatBytes(MAX_UPLOAD_BYTES)}
                    </span>
                  </label>

                  {file && (
                    <p className="picked">
                      <span className="dot" aria-hidden="true" />
                      {file.name} · {formatBytes(file.size)}
                    </p>
                  )}

                  <button className="btn" type="button" disabled={!file} onClick={onSeparate}>
                    Separate
                  </button>
                </>
              )}
            </div>
          </div>
        </section>

        <section className="band" id="how">
          <div className="wrap">
            <h2>How it works</h2>
            <div className="grid">
              {STEPS.map(({ n, title, body }) => (
                <article className="step" key={n}>
                  <span className="num">{n}</span>
                  <h3>{title}</h3>
                  <p>{body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="band" id="tiers">
          <div className="wrap">
            <h2>Tiers</h2>
            <div className="grid two">
              {TIERS.map(({ name, state, live, points }) => (
                <article className={live ? 'tier live' : 'tier'} key={name}>
                  <div className="tier-head">
                    <h3>{name}</h3>
                    <span className={live ? 'badge on' : 'badge'}>{state}</span>
                  </div>
                  <ul>
                    {points.map((point) => (
                      <li key={point}>{point}</li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="band" id="next">
          <div className="wrap">
            <h2>
              Planned <span className="badge">Not built yet</span>
            </h2>
            <div className="grid">
              {ROADMAP.map(({ title, body }) => (
                <article className="step muted" key={title}>
                  <h3>{title}</h3>
                  <p>{body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer>
        <div className="wrap">
          Local demo build · Basic model · not a production service. Sections marked
          <span className="badge">Planned</span> are not implemented.
        </div>
      </footer>

      {authOpen && (
        <div className="modal" onClick={() => setAuthOpen(false)}>
          <form
            className="panel auth"
            role="dialog"
            aria-modal="true"
            aria-label={newAccount ? 'Create an account' : 'Sign in'}
            onClick={(event) => event.stopPropagation()}
            onSubmit={onAuthSubmit}
          >
            <h2>{newAccount ? 'Create an account' : 'Sign in'}</h2>

            {authError && (
              <p className="error" role="alert">
                {authError}
              </p>
            )}

            <label className="field">
              <span>Email</span>
              <input name="email" type="email" autoComplete="username" required />
            </label>
            <label className="field">
              <span>Password</span>
              <input
                name="password"
                type="password"
                autoComplete={newAccount ? 'new-password' : 'current-password'}
                minLength={MIN_PASSWORD_LENGTH}
                required
              />
            </label>

            <button className="btn" type="submit" disabled={authBusy}>
              {authBusy ? 'Working…' : newAccount ? 'Create account' : 'Sign in'}
            </button>

            <p className="hint">
              {newAccount ? 'Already have an account? ' : 'New here? '}
              <button
                className="link"
                type="button"
                onClick={() => {
                  setNewAccount(!newAccount)
                  setAuthError('')
                }}
              >
                {newAccount ? 'Sign in' : 'Create one'}
              </button>
            </p>
            <p className="hint">
              Accounts are local to this machine and unlock nothing yet — separating a
              track works signed out.
            </p>
          </form>
        </div>
      )}
    </>
  )
}
