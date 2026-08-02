# DEC-0010 — Phase 3 auth mechanism and task split

Status: **Proposed — pending Nadav decision. Authorizes no code.**
Not an implementation authorization. Not production-approved. No public users. No commercial approval.

Phase: 3 (Auth + User Account Foundation) · Package: **none — no `PKG-P3` exists** (§9 B1)
Recorded by: the Phase 3 readiness gate run after the FAST-DEMO track closed
Relates to: `DEC-0002` (minimal code), `DEC-0005` (DB base / migration determinism), `DEC-0006` (domain
data contract), `DEC-0007` (schema contract), `DEC-0009` (demo precedent for flat modules and in-module
schemas), `docs/coding-rules.md` §2, §5, §9
Baseline (read-only historical): `stemspace-dev-pack-v0.1/phases/PHASE-03-auth-user-account-foundation.md`,
`06-security-permissions-and-secrets.md`, `10-open-decisions-and-blockers.md`

> This record exists because **Phase 3 cannot be implemented without decisions that no artifact in the
> project makes**. A search of the entire Dev Pack for `jwt`, `bcrypt`, `argon2`, `passlib`,
> `session cookie`, `httponly` and `oauth` returns **zero** matches: the phase file lists *"Password
> hashing"* and *"Backend permission guard"* as tasks but never says how either works.
> `docs/coding-rules.md` §9 forbids the code agent from deciding that for itself, so the decisions are
> proposed here for an authority to accept or change. **DEC-0010 authorizes no code.**

## 1. Decision

Implement Phase 3 as an **opaque, server-side session** system with **stdlib-only** cryptography, split
into four sequenced tasks (§10). No new backend dependency, no signing-key secret, no OAuth.

## 2. Decisions — proposed values

Each row is a decision an authority must accept or replace. The rejected alternative is recorded so the
trade-off is not re-litigated later.

| # | Decision | Proposed | Rejected alternative — and why |
|---|---|---|---|
| **D1** | Session mechanism | **Opaque server-side session token**, stored in a `sessions` table, delivered as an httpOnly cookie. | **JWT.** Phase 3's own acceptance criteria require that a **blocked user cannot act**, and Phase 11 requires account deletion to take effect. A stateless JWT cannot be revoked without a server-side denylist — which is the same table, with worse properties and an extra signing-key secret to manage. |
| **D2** | Token generation / storage | `secrets.token_urlsafe(32)` (256-bit, 43 chars). The DB stores **only the SHA-256 hex** of the token. | Storing the token itself. A database leak would then hand over live sessions. |
| **D3** | Password hashing | **`hashlib.scrypt`** (stdlib): `n=2**14, r=8, p=1, dklen=32`, 16-byte random salt per password. Stored as one self-describing string `scrypt$n$r$p$<salt-b64>$<hash-b64>` so parameters can be raised later without a migration. Verified with `hmac.compare_digest`. | **bcrypt / argon2 / passlib.** Each adds a backend dependency, which invalidates the cached pip layer and forces a full reinstall **including torch** behind a TLS-intercepting proxy — a known failure mode in this environment. `DEC-0009` §8 rejected `python-multipart` for exactly this reason. Availability is **verified**, not assumed (see *Runtime facts*). |
| **D4** | Cookie flags | `httponly=True`, `samesite="lax"`, `path="/"`; `secure=True` unless `APP_ENV == "local"`. | Token in a response body, in `localStorage`, or in a URL. All three expose the token to scripts, logs or referrers. |
| **D5** | Lifetime | **Absolute 7 days**, no sliding renewal. Logout deletes the row. Expired rows are deleted lazily when looked up. | A background sweeper or scheduler. `DEC-0009` §7 already set the precedent that minimal, inline cleanup is sufficient at this stage. |
| **D6** | Signup policy | **Open signup** with email + password. **No email verification, no password reset** in Phase 3 — both are named out of scope by `PHASE-03` *"What not to change"*. | Invite-only. Nothing in the baseline calls for it, and it would add an admin surface that Phase 10 owns. |
| **D7** | Login failure disclosure | One generic message and one status (`401`) for both unknown email and wrong password, and a **dummy verification runs for an unknown email** so response time does not disclose whether an account exists. | Distinct messages / early return. Both are account-enumeration oracles. |
| **D8** | Login rate limiting | A minimal **in-process** fixed-window counter (10 attempts / 15 min per email). Explicitly **not** multi-process safe; Redis-backed limiting belongs to Phase 12. | Redis now. Phase 3 must not pull queue/broker infrastructure forward. **This row may be deferred entirely** without blocking D1–D7. |
| **D9** | Placement | A **flat module** `backend/app/auth.py` holds the routes, the guard and its request/response models. | `app/api/`, `app/routers/`, `app/services/` — an existing P2-003 test asserts their absence. Defining the models in-module also keeps `DEC-0007`'s closed class set closed (§7). |

**No decision outside this table is made here.** If implementation appears to need one, that is a
**blocker to raise**, not a choice for the code agent (`coding-rules.md` §9).

## 3. Data model additions

Added to the existing `users` table (`DEC-0006` §4.1 deliberately left these to Phase 3):

| Column | Type | Notes |
|---|---|---|
| `password_hash` | `String(255)`, NOT NULL | The D3 encoded string. Never returned by any route. |
| `profile_visibility` | `String(16)`, NOT NULL, default `'hidden'` | `CHECK IN ('hidden','public')`. Private by default. |
| `preferred_language` | `String(8)`, NULL | BCP-47 short tag. No default — the UI decides. |
| `email_opt_in` | `Boolean`, NOT NULL, default `false` | Opt-**in**, so the default must be false. |

`status` (`active` / `blocked` / `deleted`) already exists and is reused unchanged.

New table `sessions`:

| Column | Type | Notes |
|---|---|---|
| `id` | `Uuid` PK | |
| `user_id` | `Uuid` FK → `users.id`, NOT NULL, indexed | |
| `token_hash` | `String(64)`, NOT NULL, **unique** | SHA-256 hex of the token (D2). |
| `created_at` / `expires_at` | tz-aware `DateTime` | UTC-aware per `DEC-0006` §3. |

No `revoked_at`: logout **deletes** the row, which is simpler and leaves nothing to interpret.

## 4. Route contract

Four routes, all under `/auth`, in the flat module of D9:

- `POST /auth/signup` → `201`, sets the session cookie, returns the public user shape.
- `POST /auth/login` → `200`, sets the session cookie.
- `POST /auth/logout` → `204`, deletes the session row and clears the cookie.
- `GET /auth/me` → `200` with the current user, or `401`.

The guard is one FastAPI dependency (`current_user`): `401` when the cookie is missing, unknown or
expired; `403` when the user's `status` is not `active`.

`backend/tests/test_health.py::test_no_out_of_scope_routes` must be **deliberately re-scoped** to allow
`/auth/*` — exactly the treatment `/demo/*` received in FAST-DEMO-003 — while still forbidding `/songs`,
`/library` and `/admin`. It must not be deleted or weakened further.

## 5. Security properties (binding)

- The password, the stored hash and the session token appear in **no** response body, log line, error
  message, metric or schema. `UserRead` gains **no** credential field.
- No secret is added to the repo, and **D1 requires no signing key** — there is nothing to rotate.
- Errors carry fixed, safe text: no traceback, no echo of submitted input, no path.
- Backend-enforced authorization only; a UI-only restriction is never sufficient
  (`06-security-permissions-and-secrets.md`, `coding-rules.md` §3).
- `profile_visibility = 'hidden'` must never be returned publicly. The column lands here; the public
  surface that must respect it is Phase 9.

## 6. Out of scope for Phase 3

OAuth / social login, password reset, email verification, admin or RBAC, quotas and coupons, upload,
storage, queue/worker, public library, ratings, Professional. Phase 3 adds **accounts and a guard** —
nothing that consumes them yet.

## 7. Relationship to the closed Phase 2 contracts

- `DEC-0006` §4.1 states *"No password / auth-credential columns in P2 — authentication (password hash,
  sessions, tokens) is Phase 3 and is not designed here."* This record is that design. `DEC-0006` needs a
  **pointer**, not an amendment.
- `DEC-0007` **closes** the `app/schemas/` class set, and a P2-003 test asserts it. D9 therefore defines
  the auth request/response models **inside `app/auth.py`**, so `DEC-0007` stays closed and the existing
  test keeps passing with no amendment. This is the same device `DEC-0009` §5 used for the demo.

## 8. Testing contract

Required across the four tasks:

1. Hash/verify round-trip; the same password hashes differently twice (random salt).
2. No plaintext password is stored, and the encoded hash never appears in a response.
3. Signup → login → `/auth/me` happy path; the cookie is `httponly`.
4. A `blocked` and a `deleted` user are refused by the guard (`403`), an unknown/expired session `401`.
5. Unknown email and wrong password are indistinguishable in status and body (D7).
6. No credential, token or path appears in any response or error body.
7. Migration determinism per `DEC-0005`; DB tests run on SQLite in-memory per `DEC-0008`.
8. The re-scoped route-boundary test still forbids `/songs`, `/library`, `/admin`.
9. Every Phase 0/1/2 and FAST-DEMO regression still passes, unchanged.

## 9. Blockers this record does NOT close

| # | Blocker | Owner |
|---|---|---|
| **B1** | The Dev Pack has **no `PKG-P3` and no `tasks/phase-3/`** — only P0–P2 exist. §10 supplies repo-local stubs instead, the same way the FAST-DEMO track did. | Eitan / Nadav |
| **B2** | `PHASE-03` is `Status: DRAFT — NOT APPROVED`, `Execution allowed: No`, `Phase readiness label: Security Review Required`. | Nadav |
| **B3** | **OD-003** (Noa security/API confirmation) and **OD-001** (PRD V1.1 confirmation) are still open in `10-open-decisions-and-blockers.md`. D1–D9 are proposals *pending* exactly that review. | Noa / Mika |
| **B4** | Phase 3 is the first phase that actually **runs migrations against Postgres**. Locally, host port `5432` is already in use, so `POSTGRES_PORT` must be overridden in the git-ignored `.env`. | Operator |

B1–B3 are authority blockers: they gate **authorization**, not implementation difficulty. B4 is
operational and takes one line of local config.

## 10. Task split

| Task | Scope | Writes |
|---|---|---|
| **P3-001** | User auth columns + `sessions` table + one Alembic migration. **No routes, no hashing logic.** | `app/db/models.py`, `alembic/versions/*`, `tests/db/*` |
| **P3-002** | Password hashing and session-token helpers as **pure functions** (D2, D3, D7's dummy verify). **No routes, no DB.** | `app/auth.py` (helpers only), `tests/*` |
| **P3-003** | The four `/auth` routes + the `current_user` guard + the re-scoped boundary test. | `app/auth.py`, `app/main.py`, `tests/*` |
| **P3-004** | Frontend auth: sign-up / sign-in form, `/auth/me` bootstrap, sign-out — replacing the inert `Sign in` control currently on the demo page. | `frontend/src/api/*`, `frontend/src/*` |

Executed **one at a time**, in order, each with an evidence report and a stop gate between them
(`coding-rules.md` §9). P3-001 and P3-002 are independent of each other; P3-003 needs both.

## 11. Authorization boundary

- **DEC-0010 authorizes no code.** No column, migration, route, guard, module or commit follows from
  this record alone. Each P3 task begins only after Nadav reviews this record and issues an explicit
  implementation authorization for that task.
- Where this record and the read-only Dev Pack differ **for Phase 3**, this record wins once approved;
  the Dev Pack remains authoritative for everything it does not supersede.
- The decisions here are **Phase 3 scoped**. They do not amend `coding-rules.md`, `DEC-0003`,
  `DEC-0006` or `DEC-0007`, and the `DEC-0009` demo deviations remain non-precedential and expired.

## Runtime facts verified (informative)

Checked inside the current backend image so the D3 implementer does not have to re-derive them:

- **`hashlib.scrypt` is available** — Python **3.12.13**, OpenSSL **3.5.6**. `hmac.compare_digest` and
  `secrets.token_urlsafe(32)` (43 characters) likewise.
- Therefore **D1–D3 need no new dependency**, the cached pip layer stays intact, and no torch reinstall
  is triggered.
- The backend suite currently stands at **281 passed, 1 skipped**; Phase 3 must not regress it.

## Rationale

The Phase 3 readiness gate found the phase blocked on decisions rather than on difficulty: the acceptance
criteria are clear, the `User` table already exists, and the guard is a few dozen lines. What was missing
was any statement of *how* sessions and hashing work — and under `coding-rules.md` §9 the code agent may
not invent that.

Proposing the answers here, with the rejected alternatives and their reasons attached, converts Phase 3
from "blocked on an unknown" into a mechanical four-task sequence. Choosing opaque sessions over JWT is
what makes the phase's own *"blocked user cannot act"* criterion enforceable at all, and choosing stdlib
scrypt over a hashing library is what keeps the phase from tripping the dependency failure mode that this
project has already hit once.
