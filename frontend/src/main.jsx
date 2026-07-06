import React from 'react'
import ReactDOM from 'react-dom/client'

import App from './App.jsx'
import './index.css'

// Phase 0 shell entry point — mounts the placeholder App. No routing, no state
// management, no API client (P0-005 minimal-code boundary).
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
