# P3-003 — Auth routes and permission guard

Status: **PLANNING STUB — NOT AUTHORIZED YET. Requires an explicit Nadav prompt. Do not implement yet.**
Track: Phase 3 (Auth + User Account Foundation) · Package: none (no `PKG-P3` exists)
Depends on: **P3-001 and P3-002 complete and accepted** ·
**`docs/decisions/DEC-0010-phase-3-auth-contract.md` accepted** (the contract for this task)
Relates to: `DEC-0007` (closed schema class set), `DEC-0009` §5 (flat-module / in-module-schema precedent)

> **Do not implement yet.** This stub records *what this task will be* so the work can start mechanically
> when authorized — it authorizes **nothing**. Implement **exactly** the DEC-0010 contract; do not
> re-decide it (`docs/coding-rules.md` §9).

## Goal

The four `/auth` routes and the single backend-enforced guard that later phases depend on.

## Contract (fixed by DEC-0010 §4, D1, D4, D5, D8 — do not re-decide)

- `POST /auth/signup` → `201` + session cookie · `POST /auth/login` → `200` + session cookie ·
  `POST /auth/logout` → `204`, row deleted · `GET /auth/me` → `200` or `401`.
- Cookie: `httponly`, `samesite=lax`, `path=/`, `secure` unless `APP_ENV == "local"`.
- Absolute 7-day lifetime, no sliding renewal; expired rows deleted lazily on lookup — no sweeper.
- Guard `current_user`: `401` for missing/unknown/expired session, `403` when `status != 'active'`.
- Request/response models live **inside `app/auth.py`**, so `DEC-0007`'s closed class set stays closed.
- Optional and deferrable: the D8 in-process login rate limiter.

## What NOT to build

- No OAuth, social login, password reset or email verification (`PHASE-03` *"What not to change"*).
- No admin, RBAC, quota check, upload, storage, queue or public surface.
- No class added to `app/schemas/` and no new directory under `app/`.
- No token in a response body, a URL or `localStorage`; no password/hash/token in any log or error.

## Files likely to change

- `backend/app/auth.py`, `backend/app/main.py`
- `backend/tests/test_health.py` — the route-boundary test is **deliberately re-scoped** to allow
  `/auth/*` (as FAST-DEMO-003 did for `/demo/*`) while still forbidding `/songs`, `/library`, `/admin`.
  It must not be deleted or weakened further.
- `backend/tests/*`

## Required checks (when authorized)

1. `docker compose run --rm --no-deps backend python -m pytest -q` — no regression.
2. Signup → login → `/auth/me` happy path; cookie is `httponly`.
3. `blocked` and `deleted` users are refused (`403`); unknown/expired session gives `401`.
4. Unknown email and wrong password are indistinguishable in status **and** body (D7).
5. No credential, token or path appears in any response or error body.
6. `docker compose run --rm --no-deps worker python -m app.worker --check` still passes.

## Evidence to return

Changed files · checks run · the exact re-scoping applied to the boundary test · confirmation that **no
dependency was added** · deviations · blockers.

## Stop gate

Stop after this task. Do not start P3-004. Return the evidence report and wait for review.
