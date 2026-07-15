# P2-000 — Phase 2 Readiness Fixes / Decision Record

Status: **EXECUTED — documentation / decision-record only. Pending Nadav review before P2-001.**
Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2
Baseline: `stemspace-dev-pack-v0.1/phases/PHASE-02-backend-domain-db-skeleton.md`,
`stemspace-dev-pack-v0.1/packages/PKG-P2-backend-domain-db-skeleton.md`,
`stemspace-dev-pack-v0.1/tasks/phase-2/*`

> **Documentation only.** This task changed **no** runtime code, installed **no** dependencies,
> created **no** database models or migrations, and opened **no** database connection. It does not
> authorize P2-001.

## Goal

Fix the Phase 2 readiness documents so that **P2-001 can later be safely authorized as a separate
implementation task**, without requiring the code agent to invent DB architecture, breach its own
write scope, or guess at its definition of done.

## Context — what this fixes

The Phase 2 readiness / discovery gate reported **BLOCKED** for five reasons:

1. **Missing Phase 2 authorization** — every Phase 2 artifact carries `Execution allowed: No`.
2. **P2-001 write-scope gap** — the task's acceptance criterion ("Alembic env loads") was
   unreachable, because `backend/requirements.txt` carries no SQLAlchemy/Alembic/psycopg and was
   **outside** the task's declared write scope.
3. **Missing DB architecture decisions** — sync vs async session, base style, constraint naming
   convention (required for the deterministic migrations PKG-P2 mandates), and where the DB URL is
   read were all undefined.
4. **Missing test contract** — the sole required test, "migration scaffold test", was never defined.
5. **Security clarifications** — checkpoint/local paths in DB, the `SignedUrlGrant` vs
   "signed URLs are not stored in DB" conflict, and `DATABASE_URL` leaking through error output were
   unaddressed.

Items 2–5 are fixed here. **Item 1 is not fixed here** and cannot be: authorization is Nadav's to
give, and this task's output is what that review evaluates.

## Scope

Documentation and decision records only, inside the repo-local `docs/` tree.

## What to build

- `docs/decisions/DEC-0005-db-base-session-and-migration-determinism.md` — record the DB stack,
  session style, base style, naming convention, config/DB-URL path, dependency set, security rules,
  test contract, out-of-scope list and authorization boundary.
- `docs/tasks/phase-2/P2-001-db-base-and-alembic.md` — a repo-local task doc that is **executable
  later** without inventing architecture: widened write scope, explicit stack, explicit dependency
  list, explicit tests/evidence, explicit do-not-build list and stop gate.
- `docs/tasks/phase-2/P2-002-domain-models.md` — security guardrails that block unsafe model design.
- `docs/tasks/phase-2/P2-003-pydantic-schemas-no-storage-key-leak.md` — storage-key / private-field
  schema guardrails.
- `docs/tasks/phase-2/P2-004-seed-tags-and-db-tests.md` — DB test alignment and a blocker rule for
  missing state/idempotency decisions.
- `docs/tasks/phase-2/P2-000-readiness-fixes.md` — this document.
- Short Phase 2 status notes in `README.md` and `docs/README.md`.

## What not to build

- **No P2-001 implementation.** No DB base, no session, no Alembic config, no `env.py`.
- No runtime code of any kind; no database models; no migrations.
- No ORM dependencies added; **no packages installed**; `backend/requirements.txt` untouched.
- No Alembic run; no PostgreSQL connection.
- No API routes; no upload flow; no queue processing; no Redis; no MinIO/S3.
- No AI inference connected to the app flow.
- No frontend changes; no worker behavior changes.
- No Phase 3 work.
- **No modification of the source Dev Pack** (`stemspace-dev-pack-v0.1/*`) — it is the read-only
  source of truth; repo-local docs adapt it.
- No commit until review is complete.

## Decisions recorded

Captured in **DEC-0005** (full detail there):

| Area | Decision |
|---|---|
| Stack | PostgreSQL, sync SQLAlchemy, Alembic, psycopg3 sync driver; Pydantic stays the schema layer, not the DB layer |
| Session | Sync `Session`/`sessionmaker`; no async SQLAlchemy in P2-001; DB imports open no connection at import time |
| Base | `DeclarativeBase` + one shared `MetaData` with a naming convention; no overbuilt mixin hierarchy |
| Naming convention | Explicit `ix`/`uq`/`ck`/`fk`/`pk` patterns; no backend-generated random constraint names |
| DB URL | Extend `backend/app/config.py` with a repr-hidden `database_url`; no direct `os.getenv` in DB modules; missing URL fails safely; **`DATABASE_URL` must not be logged or echoed** |
| Dependencies | P2-001 may edit `backend/requirements.txt`; `sqlalchemy`, `alembic`, `psycopg[binary]` only; no redis/celery/boto3/minio/storage/queue deps |
| Security | **no checkpoint/model/local filesystem paths in DB**; no `LOCAL_MODEL_ROOT` in DB; **no signed URL string in DB**; `SignedUrlGrant` stores grant/audit metadata only; **no audio bytes in DB**; no public storage URLs; **`storage_key` must not be exposed** in client/API schemas |
| Tests | Eight-point explicit contract replacing the undefined "migration scaffold test" |

**Widened P2-001 write scope** (the fix for the blocking scope gap):

- `backend/requirements.txt`
- `backend/app/config.py`
- `backend/app/db/`
- `backend/alembic.ini`
- `backend/alembic/`
- `backend/tests/` (repo style: `backend/tests/db/`)

## What P2-000 does NOT decide

These remain **open** and still block **P2-002**, not P2-001:

- **Song / SeparationJob state values** — named nowhere in the pack; a product decision.
- **Field-level definitions for the 14 entities** — the pack names entities and specifies zero
  fields; created/updated timestamps are never mentioned.
- **UsageEvent idempotency/uniqueness key** — "unique success finalization by song" is an intent,
  not a key.
- **`storage_key` format and owning entity** — the rule that it stays internal is clear; its shape
  is not.
- **Default tag taxonomy** (P2-004).

Phase 2 also still does **not** authorize: upload API, queue processing, AI processing, storage
client, signed URL generation, frontend UI, worker processing, production DB, public users, or
auth/billing/admin/public library/resumable upload/extra stems.

## Acceptance criteria

1. DEC-0005 exists and records the DB session/style/config/dependency/security/test decisions.
2. The P2-001 doc is executable later **without** the code agent inventing DB architecture.
3. The P2-001 write scope includes the required dependency/config files.
4. The P2-001 test contract is explicit.
5. P2-002 / P2-003 / P2-004 docs carry guardrails that prevent unsafe DB/schema design.
6. Docs explicitly forbid checkpoint/local paths in DB.
7. Docs explicitly forbid signed URL strings in DB.
8. Docs explicitly forbid audio bytes in DB.
9. Docs explicitly prevent `storage_key` exposure in client/API schemas.
10. No runtime code is modified.
11. No dependencies are installed.
12. No migrations are created.
13. The source Dev Pack is not modified.
14. Work stops after P2-000.

## Evidence expected

- `git status --short` — changed files are **docs-only** and within the allowed scope.
- No `backend/*`, `frontend/*`, `docker-compose.yml`, `backend/requirements.txt`,
  `backend/Dockerfile` or `.env.example` changes.
- `git status --short -- stemspace-dev-pack-v0.1` — **empty**.
- Changed docs contain **no personal/local machine paths** and no real secrets.
- Changed docs contain the required security statements.
- No app tests run: this is docs-only, and running them would require a dependency install that is
  explicitly out of scope.

## Stop gate

Stop after P2-000. Do not implement P2-001. Do not commit until review is complete.
P2-001 begins only after **Nadav reviews this P2-000 result** and issues an explicit implementation
authorization.
