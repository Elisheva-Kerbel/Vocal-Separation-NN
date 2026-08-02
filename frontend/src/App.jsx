// StemSpace local demo page (FAST-DEMO-004) — LOCAL DEMO ONLY.
//
// One page. The upload -> separate -> compare flow is REAL and runs against the
// local Basic model. Everything else on the page is presentation, and anything not
// built yet is labelled `Planned` rather than mocked up as if it worked: no invented
// price, no fake library rows, no sign-in that pretends to authenticate. That keeps
// the richer product framing honest about what exists (DEC-0009 §4 — no production
// claim, and Professional must never be shown as implemented).
//
// Plain React + CSS, no UI library, no new dependency (DEC-0009 D8). Every backend
// call goes through ./api/demo.js (docs/coding-rules.md §2).
import { useEffect, useRef, useState } from 'react'

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
  { title: 'Accounts', body: 'Sign-up, sign-in and per-user permissions.' },
  { title: 'Cloud library', body: 'Your tracks and stems, kept privately across sessions.' },
  { title: 'Background processing', body: 'Queue long jobs instead of waiting on the request.' },
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
  const [file, setFile] = useState(null)
  const [sourceUrl, setSourceUrl] = useState('')
  const [stems, setStems] = useState(null)
  const [active, setActive] = useState('original')
  const [busy, setBusy] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState('')
  const players = useRef({})

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
            <button className="ghost" type="button" disabled title="Planned — accounts are not built yet">
              Sign in
            </button>
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
    </>
  )
}
