# FAST-DEMO-004 — Frontend Demo UI

Status: **PLANNING STUB — NOT AUTHORIZED YET. Requires an explicit Nadav prompt. Do not implement yet.**
Track: FAST-DEMO (local demo vertical slice) · Package: none
Depends on: **FAST-DEMO-003 complete and accepted** ·
**`docs/decisions/DEC-0009-local-demo-vertical-slice.md`** (the contract for this task)
Relates to: `DEC-0002`, `DEC-0004`, `docs/coding-rules.md` §2

> **Do not implement yet.** This document is a planning stub. It records *what this task will be* so the
> work can start mechanically when authorized — it authorizes **nothing** on its own. No component, no
> style, no API module and no commit may be produced until Nadav issues an explicit FAST-DEMO-004
> implementation prompt, and not before FAST-DEMO-003 is accepted. Implement **exactly** the DEC-0009
> contract; do not re-decide it (`docs/coding-rules.md` §9).

## Goal

Replace the Phase 0 static shell with **one clean page** that uploads a file, shows a processing state,
and presents Vocals + Background — clean and intentional, not overbuilt.

## Contract (fixed by DEC-0009 §6 — do not re-decide)

Three states, nothing more:

- **Upload / select** — one file input, visible constraints (accepted formats, size cap, expected wait),
  and a **"Basic · local demo"** label so the demo cannot be mistaken for a product tier or production.
- **Processing** — indeterminate indicator plus honest copy. **No fake progress**: no invented
  percentage, no simulated ETA.
- **Result** — exactly **two** audio players (Vocals, Background) with download links, plus a reset to
  run another file.
- **Error** — one inline, safe message; the page stays usable.

## What to build (when authorized)

- The single page in `frontend/src/`, styled with plain CSS.
- A small `frontend/src/api/` module — **all** backend calls go through it (`coding-rules.md` §2); no
  API logic and no business logic inside components.
- Whatever minimal dev-server wiring is needed to reach the backend from the browser (a Vite dev proxy
  is preferred over CORS changes, since it keeps the backend untouched and exposes no origin config).

## What NOT to build

- **No new npm dependency** — plain React + CSS (DEC-0009 §3 D8). A dependency change forces an
  in-container `npm install`, a known failure mode behind a TLS-intercepting proxy.
- No login/auth UI, library or history, admin, payment/billing/quota UI, sharing or ratings.
- **No Professional selector** and no tier chooser of any kind — Professional is not implemented.
- No fake progress bar, no invented metrics, no placeholder screens for unbuilt features.
- No storage key, checkpoint reference, local path, internal error text or environment value rendered in
  the UI or stored in the browser.
- No backend change, no worker change, no Docker image dependency change.

## Files likely to change

- `frontend/src/App.jsx`, `frontend/src/index.css` — the demo page.
- `frontend/src/api/<demo client>.js` — **new**.
- `frontend/vite.config.js` — only if a dev proxy is required.

## Required checks (when authorized)

1. `docker compose run --rm --no-deps frontend npm run build` — passes, **with no new dependency**.
2. `git diff` on `frontend/package.json` / `package-lock.json` — **empty**.
3. Manual: the three states render correctly, including the error state.
4. Backend suite still green (the frontend task must change no backend behavior).

## Evidence to return

Changed files · checks run · manual verification of the three states · deviations · blockers ·
confirmation that no dependency was added and no out-of-scope UI was built.

## Stop gate

Stop after this task. Do not start FAST-DEMO-005. Return the evidence report and wait for review.
