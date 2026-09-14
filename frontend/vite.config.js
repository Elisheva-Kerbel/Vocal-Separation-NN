import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Minimal Vite config for the local demo page (P0-005, extended by FAST-DEMO-004).
//
// server.host binds the dev server to 0.0.0.0 inside the container so it is
// reachable from the host; server.port fixes the port that docker-compose maps
// via FRONTEND_PORT.
//
// server.proxy forwards the demo and auth routes to the backend over Compose's
// internal network, so the browser only ever sees same-origin `/demo/...` and
// `/auth/...` URLs. Same-origin is what makes the session cookie work at all: a
// SameSite=Lax httpOnly cookie set by the backend is sent back on same-origin
// requests without the frontend ever touching it. A dev proxy is used instead of
// CORS config so the backend stays untouched and no backend origin, port or env
// value is exposed to the browser bundle. `backend:8000` is the Compose service
// name and its fixed container port — not a host path or a secret.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/demo': 'http://backend:8000',
      '/auth': 'http://backend:8000',
      '/upload': 'http://backend:8000',
      '/songs': 'http://backend:8000',
      '/library': 'http://backend:8000',
      '/public': 'http://backend:8000',
      '/coupons': 'http://backend:8000',
      '/admin': 'http://backend:8000',
      '/settings': 'http://backend:8000',
      '/health': 'http://backend:8000',
      '/quota': 'http://backend:8000',
      '/subscriptions': 'http://backend:8000',
    },
  },
})
