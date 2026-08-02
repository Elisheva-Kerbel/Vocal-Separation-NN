# P3-001 — User auth columns and sessions table

Status: **PLANNING STUB — NOT AUTHORIZED YET. Requires an explicit Nadav prompt. Do not implement yet.**
Track: Phase 3 (Auth + User Account Foundation) · Package: none (no `PKG-P3` exists)
Depends on: **`docs/decisions/DEC-0010-phase-3-auth-contract.md` accepted** (the contract for this task)
Relates to: `DEC-0005` (migration determinism), `DEC-0006` (domain data contract), `DEC-0008` (DB test policy)

> **Do not implement yet.** This stub records *what this task will be* so the work can start mechanically
> when authorized — it authorizes **nothing**. Implement **exactly** the DEC-0010 contract; do not
> re-decide it (`docs/coding-rules.md` §9).

## Goal

Give the existing `users` table the four account columns Phase 3 needs, and add the `sessions` table —
schema only. **No routes, no hashing logic, no guard.**

## Contract (fixed by DEC-0010 §3 — do not re-decide)

- `users` gains `password_hash`, `profile_visibility`, `preferred_language`, `email_opt_in` with exactly
  the types, nullability, defaults and check constraint listed in DEC-0010 §3.
- New `sessions` table with `id`, `user_id`, `token_hash` (unique), `created_at`, `expires_at`.
- Timestamps are UTC-aware and reuse the existing mixins (`DEC-0006` §3). No new `Base`, no second
  `MetaData`, no async.
- One Alembic migration, deterministic per `DEC-0005`.

## What NOT to build

- No route, no request/response model, no hashing, no token generation, no guard — those are P3-002/003.
- No change to `app/schemas/` (its class set is closed by `DEC-0007` and asserted by a test).
- No new directory (`app/api/`, `app/routers/`, `app/services/` are asserted absent).
- No seed user, no fixture account, no default password anywhere.

## Files likely to change

- `backend/app/db/models.py`
- `backend/alembic/versions/<new migration>.py` — **new**
- `backend/tests/db/*`

## Required checks (when authorized)

1. `docker compose run --rm --no-deps backend python -m pytest -q` — no regression (baseline 281 passed, 1 skipped).
2. `pytest tests/db -q` — new column/constraint coverage passes.
3. Migration determinism per `DEC-0005`; DB tests on SQLite in-memory per `DEC-0008`.
4. No credential value, default password or path appears in any test output.

## Evidence to return

Changed files · checks run · migration id · deviations · blockers · confirmation that no route, no
hashing and no schema-layer class was added.

## Stop gate

Stop after this task. Do not start P3-002. Return the evidence report and wait for review.
