// Local demo page (FAST-DEMO-004 / DEC-0009 §6) — LOCAL DEMO ONLY.
//
// One page, four states: idle, processing, result, error. Nothing else exists here
// by design: no login, library, pricing, admin, tier chooser or Professional
// selector, and no fake progress. Every backend call goes through ./api/demo.js.
import { useState } from 'react'

import { separate } from './api/demo.js'

const STEM_LABELS = { vocals: 'Vocals', background: 'Background' }

export default function App() {
  const [file, setFile] = useState(null)
  const [stems, setStems] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function onSeparate() {
    setBusy(true)
    setError('')
    try {
      setStems(await separate(file))
    } catch (failure) {
      setError(failure.message)
    } finally {
      setBusy(false)
    }
  }

  function onPick(event) {
    setFile(event.target.files[0] ?? null)
    setError('')
  }

  function reset() {
    setFile(null)
    setStems(null)
    setError('')
  }

  return (
    <main className="page">
      <header className="head">
        <h1>StemSpace</h1>
        <p className="tag">Basic · Local demo</p>
      </header>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {stems ? (
        <>
          {stems.map(({ stem, url }) => (
            <section className="card" key={stem}>
              <h2>{STEM_LABELS[stem] ?? stem}</h2>
              <audio controls src={url} />
              <a className="download" href={url} download={`${stem}.wav`}>
                Download
              </a>
            </section>
          ))}
          <button className="btn" type="button" onClick={reset}>
            Separate another file
          </button>
        </>
      ) : busy ? (
        <section className="card processing">
          <span className="spinner" aria-hidden="true" />
          <p aria-live="polite">
            Separating vocals and background. This can take a couple of minutes.
          </p>
        </section>
      ) : (
        <section className="card">
          <input type="file" accept="audio/mpeg,audio/wav,.mp3,.wav" onChange={onPick} />
          <p className="hint">MP3 or WAV · max 20 MB</p>
          <button className="btn" type="button" disabled={!file} onClick={onSeparate}>
            Separate
          </button>
        </section>
      )}
    </main>
  )
}
