# P3-002 — Password hashing and session tokens

Status: **PLANNING STUB — NOT AUTHORIZED YET. Requires an explicit Nadav prompt. Do not implement yet.**
Track: Phase 3 (Auth + User Account Foundation) · Package: none (no `PKG-P3` exists)
Depends on: **`docs/decisions/DEC-0010-phase-3-auth-contract.md` accepted** (the contract for this task)
Relates to: `DEC-0002` (minimal code), `docs/coding-rules.md` §5

> **Do not implement yet.** This stub records *what this task will be* so the work can start mechanically
> when authorized — it authorizes **nothing**. Implement **exactly** the DEC-0010 contract; do not
> re-decide it (`docs/coding-rules.md` §9).

## Goal

The cryptographic core of Phase 3 as **pure functions**: hash a password, verify one, mint a session
token, hash it for storage. **No routes, no DB access, no cookie handling.**

## Contract (fixed by DEC-0010 D2, D3, D7 — do not re-decide)

- `hashlib.scrypt` with `n=2**14, r=8, p=1, dklen=32` and a 16-byte random salt per password.
- Encoded as one self-describing string `scrypt$n$r$p$<salt-b64>$<hash-b64>`, so parameters can be raised
  later without a migration.
- Verification uses `hmac.compare_digest`, and a **dummy verification runs for an unknown email** so
  response time does not disclose whether an account exists (D7).
- Tokens come from `secrets.token_urlsafe(32)`; only their SHA-256 hex is ever persisted.
- **Stdlib only — no new dependency.** Availability is already verified (DEC-0010 *Runtime facts*).

## What NOT to build

- No route, no FastAPI dependency, no cookie, no DB query — those are P3-003.
- No configurable hashing backend, no algorithm registry, no "pluggable" indirection (`DEC-0002`).
- No password policy engine beyond what DEC-0010 states.
- No logging of a password, hash, token or salt — at any level, including debug.

## Files likely to change

- `backend/app/auth.py` — **new**, helper functions only (flat module; `app/api/`, `app/routers/`,
  `app/services/` are asserted absent).
- `backend/tests/*`

## Required checks (when authorized)

1. `docker compose run --rm --no-deps backend python -m pytest -q` — no regression.
2. Hash/verify round-trip; the same password hashes differently twice; a tampered encoded string fails.
3. Verification of an unknown account still performs the dummy work (D7).
4. `pytest tests/ai -q` — the AI-boundary lazy-import test still passes (this module must pull in no
   heavy dependency).
5. No credential, token or salt appears in test output.

## Evidence to return

Changed files · checks run · confirmation that **no dependency was added** · deviations · blockers ·
confirmation that no route, cookie or DB access was introduced.

## Stop gate

Stop after this task. Do not start P3-003. Return the evidence report and wait for review.
