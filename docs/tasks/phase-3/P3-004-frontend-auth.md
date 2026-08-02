# P3-004 — Frontend auth

Status: **PLANNING STUB — NOT AUTHORIZED YET. Requires an explicit Nadav prompt. Do not implement yet.**
Track: Phase 3 (Auth + User Account Foundation) · Package: none (no `PKG-P3` exists)
Depends on: **P3-003 complete and accepted** ·
**`docs/decisions/DEC-0010-phase-3-auth-contract.md` accepted** (the contract for this task)
Relates to: `docs/coding-rules.md` §2, `DEC-0009` §6 (the current demo page this task modifies)

> **Do not implement yet.** This stub records *what this task will be* so the work can start mechanically
> when authorized — it authorizes **nothing**. Implement **exactly** the DEC-0010 contract; do not
> re-decide it (`docs/coding-rules.md` §9).

## Goal

Make the inert `Sign in` control on the current page real: sign up, sign in, see who you are, sign out.

## Contract (fixed by DEC-0010 §4 — do not re-decide)

- One combined sign-up / sign-in form; email + password only.
- On load, call `GET /auth/me` once to establish session state; `401` simply means signed out.
- Sign-out calls `POST /auth/logout` and clears local state.
- The session lives **only** in the httpOnly cookie: the frontend never reads, stores or forwards a
  token, and nothing auth-related is written to `localStorage` or `sessionStorage`.
- All calls go through `frontend/src/api/*` (`coding-rules.md` §2); no business logic in components.
- Failures render one safe inline message, mapped from a fixed code — the same pattern
  `frontend/src/api/demo.js` already uses. Unknown email and wrong password must stay
  indistinguishable in the UI too (DEC-0010 D7).

## What NOT to build

- **No new npm dependency** — plain React + CSS, no form or validation library.
- No password reset, email verification, social login or "remember me".
- No library, history, admin, billing/quota UI, Professional selector or tier chooser.
- No route/page for a feature that does not exist; the `Planned` labels stay honest.

## Files likely to change

- `frontend/src/api/auth.js` — **new**
- `frontend/src/App.jsx`, `frontend/src/index.css`

## Required checks (when authorized)

1. `docker compose run --rm --no-deps frontend npm run build` — passes, **with no new dependency**.
2. `git diff` on `frontend/package.json` / `package-lock.json` — **empty**.
3. `docker compose run --rm --no-deps backend python -m pytest -q` — no regression (this is a frontend
   task and must change no backend behavior).
4. Manual: signed-out, signed-in and error states render; sign-out returns to signed-out.
5. No token, credential or path appears in any committed frontend file or in browser storage.

## Evidence to return

Changed files · checks run · manual verification of the three states · confirmation that **no dependency
was added** and no out-of-scope UI was built · deviations · blockers.

## Stop gate

Stop after this task. Phase 3 closure is a separate review. Return the evidence report and wait.
