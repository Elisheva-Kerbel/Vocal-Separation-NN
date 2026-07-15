# P2-001 — DB Base and Alembic

Status: **Draft — after P2-000 readiness fixes, pending Nadav implementation authorization.**
Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2
Depends on: Phase 0 closed · `docs/decisions/DEC-0005-db-base-session-and-migration-determinism.md` · P2-000 accepted
Baseline: `stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-001-db-base-and-alembic.md`

> **Not authorized yet. Do not implement until Nadav reviews P2-000 and issues an explicit
> authorization for P2-001.** This document makes the task *executable later*; it does not start it.
>
> Every architecture choice this task needs is **already decided** in DEC-0005. If you find yourself
> deciding one, stop and report a blocker instead.

## Source of truth — read this first

- The Dev Pack under `stemspace-dev-pack-v0.1/` is **read-only historical source**. **Do not edit the
  Dev Pack.**
- **This document and `docs/decisions/DEC-0005` are the active implementation contract for P2-001.**
- **Where this document differs from `stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-001-db-base-and-alembic.md`,
  follow this document and DEC-0005.** The differences are deliberate: the pack's write scope
  excluded `backend/requirements.txt` and `backend/app/config.py` (making its own acceptance criteria
  unreachable), and its single required test was undefined. The pack file is **not** updated to match
  — it stays as historical source.
- The Dev Pack remains authoritative for everything this document does not supersede: `AGENT.md`,
  project boundaries, PKG-P2's outcome/evidence contract, and
  `templates/evidence-report-template.md`.

## Goal

Create the SQLAlchemy DB base/session and the Alembic migration foundation for local development —
**scaffold only, no entities**.

## Approved decisions (do not re-decide)

All from `docs/decisions/DEC-0005`:

- **Stack:** PostgreSQL + **sync SQLAlchemy** + **Alembic** + **psycopg3 sync driver**.
  URL scheme `postgresql+psycopg://…` (already the placeholder in `.env.example`).
- **Session:** sync `Session` / `sessionmaker`. **No async SQLAlchemy.** No `AsyncSession`, no
  `asyncpg`.
- **Base:** `DeclarativeBase` (SQLAlchemy 2.x) + one shared `MetaData`. **No mixin hierarchy.**
- **DB URL:** read **only** through `backend/app/config.py`.
- **Minimal code** (`DEC-0002`): smallest correct scaffold; no future abstractions.

## Write scope

Widened by P2-000 so the acceptance criteria are actually reachable (this was the blocking gap):

- `backend/requirements.txt` — **only** to add the three approved dependencies below.
- `backend/app/config.py` — **only** to add the repr-hidden `database_url` field.
- `backend/app/db/`
- `backend/alembic.ini`
- `backend/alembic/`
- `backend/tests/db/` — matching the existing `backend/tests/` pytest layout.

Nothing outside this list. If the task appears to require a file not listed here, **stop and report
a blocker** — do not widen scope yourself (`docs/coding-rules.md` §9).

## Dependencies to add

Exactly these, in the existing `requirements.txt` version-range style, and **nothing else**:

```text
sqlalchemy>=2.0,<3.0
alembic>=1.13,<2.0
psycopg[binary]>=3.1,<4.0
```

**No `redis`, `celery`, `boto3`, `minio`, storage-client or queue dependencies.** They belong to
their own approved phases.

> **Build note (generic).** These additions invalidate the cached pip layer in `backend/Dockerfile`,
> so the next backend build performs a real dependency download. Behind a **TLS-intercepting proxy**
> that fetch fails unless container CA trust is configured **outside the repository**. Keep TLS
> verification on; commit no bypass flags, certificates, CA paths or proxy configuration
> (`docs/coding-rules.md` §5). If the build fails for this reason, that is an **environment
> blocker** — report it; do not work around it in the repo.

## What to do

1. **Add the three dependencies** to `backend/requirements.txt`.
2. **Extend `backend/app/config.py`** with a `database_url` field:
   - follow the existing `Settings` frozen-dataclass pattern;
   - mark it **repr-hidden** (`field(repr=False)`), exactly as `s3_access_key_id` /
     `s3_secret_access_key` already are;
   - read it from the `DATABASE_URL` environment variable;
   - **fail safely and visibly** when it is missing/empty — a clear, actionable error, no silent
     fallback and no default connection string;
   - **the error must never echo the URL or the password.**
3. **Create `backend/app/db/`** with:
   - a `DeclarativeBase` subclass bound to a **single shared `MetaData`** carrying the naming
     convention below;
   - a sync engine + `sessionmaker`, created so that **importing the module opens no connection**
     (lazy engine; no connect, no query, no network at import time).
4. **Create the Alembic scaffold** — `backend/alembic.ini`, `backend/alembic/env.py`,
   `backend/alembic/versions/` (empty, with `.gitkeep`):
   - `env.py` takes the DB URL from `config.py`, **not** from a hardcoded value and **not** from a
     direct `os.getenv`;
   - `target_metadata` is **the same shared `MetaData` object** as the base — not a copy, not a new
     instance;
   - **no migration version file is created in this task** (there are no entities to migrate).
5. **Add the tests** in the contract below.

## Naming convention (required)

The shared `MetaData` must carry exactly this convention, so migrations are **deterministic** and no
constraint name is assigned by the database backend:

| Key  | Pattern |
|------|---------|
| `ix` | `ix_%(column_0_label)s` |
| `uq` | `uq_%(table_name)s_%(column_0_name)s` |
| `ck` | `ck_%(table_name)s_%(constraint_name)s` |
| `fk` | `fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s` |
| `pk` | `pk_%(table_name)s` |

Alembic's `target_metadata` must be that same metadata, or autogenerate and runtime will drift.

## What not to do — do not build

- **No models/entities beyond the base/migration scaffold.** No `User`, `Song`, `AudioFile`,
  `SeparationJob`, `Tag` or any other entity — those are P2-002 and remain **blocked** on open state
  and field decisions. Not even "just one small one" to prove the base works.
- **No migration version files.**
- **Do not auto-run migrations at app or container startup** — no `upgrade head` in `main.py`, in an
  entrypoint, in `docker-compose.yml` or in the `Dockerfile`. Migrations are run deliberately.
- **No production DB config** — no production host, credentials or non-local default target. Local
  Compose Postgres only.
- No API routes (the existing `/health` stays the only endpoint); no service layer; no repository
  layer.
- No upload flow; no queue processing; no Redis; no Celery.
- No storage client; no MinIO/S3; no signed URL generation.
- No AI integration; no frontend changes; no worker behavior changes.
- No auth, billing, admin, public library, resumable upload, or extra stems.
- **Do not modify the source Dev Pack** (`stemspace-dev-pack-v0.1/*`).

## Security rules (binding)

- **no checkpoint/model/local filesystem paths in DB** — no column, default, comment or migration
  may store a checkpoint path, model path, weights filename or operator-machine path.
- **No `LOCAL_MODEL_ROOT` value in DB** — environment-only and out-of-band per `DEC-0004`.
- **no signed URL string in DB** — signed URLs are short-lived credentials, never persisted.
- **no audio bytes in DB** — no `LargeBinary` / `BYTEA` audio columns. Audio lives in private object
  storage; the DB holds metadata only.
- **`storage_key` must not be exposed** in client/API schemas. (No entity exists in this task; the
  rule binds from the moment one does.)
- No public bucket URLs; no public object URLs; no permanent file URLs.
- **`DATABASE_URL` must not be logged or echoed** — not in exception text, Alembic log output, test
  output, tracebacks, API responses or metrics. Report *that* it is missing, never its value.
- No real secrets anywhere: placeholders only; `.env` stays git-ignored.

## Required automated tests

All eight must pass (this replaces the source task's undefined "migration scaffold test"):

1. **Alembic config/env imports and loads** — without requiring a live database.
2. **DB URL is read through `config.py`** — not via a direct `os.getenv` in a DB module.
3. **Missing DB URL fails safely** — clear error, **and the test asserts the message does not
   contain the URL or password**.
4. **Importing `app.db` opens no DB connection** — no connection, query or network at import time.
5. **Naming convention exists and is deterministic** — the shared `MetaData` carries exactly the five
   keys above, and Alembic's `target_metadata` is that same metadata object.
6. **Dependencies import** — `sqlalchemy`, `alembic`, `psycopg`.
7. **No production DB config** — nothing in committed config targets a non-local database.
8. **Phase 0/1 regression tests still pass** — `/health`, config, worker startup, and the AI boundary
   lazy-import test (proving `ai/*` pulls no heavy runtime deps) are unaffected.

## Manual verification (only if separately approved)

Running `alembic current` / `alembic upgrade head` against **local Compose Postgres** is manual
verification and is **not** required by the automated contract. Do it only if explicitly approved,
and never against a production database.

## Evidence to return

Use `stemspace-dev-pack-v0.1/templates/evidence-report-template.md`:

- changed files;
- checks/tests run, with output;
- manual verification result (or a note that it was not authorized);
- deviations;
- blockers;
- confirmation that no out-of-scope work was done — specifically: no entities, no migration version
  files, no startup auto-migration, no production DB config, no dependency beyond the approved three.

## Definition of done

- DB base, sync session config and Alembic scaffold exist within the write scope.
- All eight required tests pass.
- No production risk; no out-of-scope work.
- Evidence returned.

## Stop gate

Stop after this task. Run only approved checks. Do not continue to P2-002 — it is **blocked** on the
open Song/SeparationJob state values and entity field definitions, which are product decisions and
are **not** granted by this task or by DEC-0005. Return changed files, checks, evidence, deviations
and blockers, and wait for review.
