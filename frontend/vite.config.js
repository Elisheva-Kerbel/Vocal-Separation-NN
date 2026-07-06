import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Minimal Vite config for the Phase 0 frontend empty shell (P0-005).
//
// server.host binds the dev server to 0.0.0.0 inside the container so it is
// reachable from the host; server.port fixes the port that docker-compose maps
// via FRONTEND_PORT. No proxy, no backend API wiring, no env exposure — the
// shell makes no backend calls in Phase 0.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
  },
})
