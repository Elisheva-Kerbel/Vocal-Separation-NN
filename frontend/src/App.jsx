// Phase 0 frontend empty shell (P0-005).
//
// Static placeholder only. It exists to prove the frontend service builds and
// runs under Docker Compose. It deliberately implements NO product flow: no
// upload, result, dashboard, auth, public library, admin, billing or audio
// playback, and it makes NO backend API calls and stores no files/tokens/secrets.
export default function App() {
  return (
    <main className="shell">
      <h1>StemSpace</h1>
      <p>Phase 0 frontend shell</p>
      <p>No upload flow implemented yet.</p>
    </main>
  )
}
