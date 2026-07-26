# StemSpace — Vocal Removing Platform

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**
Source baseline: `stemspace-dev-pack-v0.1/` (STEMSPACE-DEV-PACK-001 v0.1) — **read-only historical
source; do not edit it.** For **Phase 2**, the active implementation contract is the repo-local
`docs/tasks/phase-2/*` and `docs/decisions/DEC-0005` (see `docs/README.md`).

## Purpose

StemSpace is a platform where a user can log in, upload audio, process it asynchronously into
**Vocals + Background**, and securely listen to / download the outputs via short-lived signed
URLs. Files are private; the backend authorizes every access.

This repository is being built in **small, testable phases**. It is **not** built in one pass.

## Current status

- **Phase 0 — closed.** Dockerized project skeleton (local development only).
- **Phase 1 — closed for Basic local prototype only** (`docs/decisions/DEC-0004`). This approves
  **no** production, **no** Professional tier, and **no** upload, queue, DB, storage or public-user
  scope.
- **Phase 2 — closed for the DB / domain skeleton** (`docs/decisions/DEC-0005`–`DEC-0008`): domain
  models, the Alembic migration, read-only schemas and seed tags exist. No upload, queue, storage,
  auth or public-user scope.
- **Fast Demo track — planning only, authorized up to `docs/decisions/DEC-0009`. FAST-DEMO-003 has not
  started.**
- **Not approved: production, commercial use, and the Professional tier.**

### Phase 0 (closed) — what it built

**Phase 0 — Dockerized Project Skeleton** created a minimal monorepo foundation that starts via
Docker Compose, with documentation and Git baseline files, and **no business logic**. See
`docs/tasks/phase-0/` for the per-task documents.

**TASK-P0-001** (skeleton, docs and Git baseline), **TASK-P0-002** (Docker Compose,
Dockerfiles and `.env.example`), **TASK-P0-003** (backend `/health` and config), **TASK-P0-004**
(worker startup stub) and **TASK-P0-005** (frontend empty shell) have been performed. The backend
serves a minimal `GET /health` smoke endpoint, the worker container runs a minimal **startup
stub** (`python -m app.worker`), and the frontend container now runs the **Vite + React empty
shell** (`frontend/src/App.jsx`) — a static Phase 0 placeholder that makes **no** backend API
calls, stores no files/tokens/secrets and implements **no** product flow. There is still **no
queue/job processing** and **no product UI**.

### Status and boundaries

Phase 0 is a **local development skeleton only**. It is:

- **not** approved for production;
- **not** approved for public users;
- **not** approved for upload processing (no upload / queue / AI flow exists yet).

PostgreSQL, Redis and MinIO run **only as local infrastructure services** — Compose starts them,
but they are **not** wired into any product flow. **Phase 1 was the AI Benchmark Harness only** and
is **closed for the Basic local prototype only**; it stays isolated from the app flow, and the
model/checkpoint remains local / out-of-band and out of Git (`docs/decisions/DEC-0004`). Repo docs
stay **Draft** until a readiness review passes; nothing here authorizes production use or a later
phase's scope.

### Phase 2 status (closed — DB / domain skeleton)

**Phase 2 — Backend Domain + DB Skeleton — is closed.** `docs/decisions/DEC-0005` fixes the DB
foundation contract (PostgreSQL + sync SQLAlchemy + Alembic + psycopg3, `DeclarativeBase` with a
deterministic naming convention, and a repr-hidden `database_url` sourced only through
`backend/app/config.py`); `DEC-0006` fixes the domain data contract, `DEC-0007` the read-only schema
contract and `DEC-0008` the seed taxonomy / DB-test policy. `docs/tasks/phase-2/` records the tasks.

P2-001 (DB base + Alembic), P2-002 (domain models), P2-003 (read schemas) and P2-004 (seed tags and DB
tests) are implemented and accepted. Phase 2 authorizes **no** upload API, queue processing, AI
processing, storage client, signed URL generation, frontend UI, worker processing, production DB or
public users. Throughout: **no audio bytes in DB**, **no checkpoint/model/local filesystem paths in
DB**, **no signed URL string in DB**, and `storage_key` stays internal and out of client/API schemas.

## Local development (Compose-first)

Local development is **Docker Compose-first** (see `docs/decisions/DEC-0001`). `docker compose`
wires these services together, reachable by **service name** (not `localhost`):

| Service    | Role                                             | Phase 0 state                     |
|------------|--------------------------------------------------|-----------------------------------|
| `postgres` | PostgreSQL database                              | runs (named volume)               |
| `redis`    | Redis broker/result backend for Celery           | runs                              |
| `minio`    | S3-compatible private object storage (local dev) | runs (named volume)               |
| `backend`  | FastAPI app                                      | serves `GET /health` (P0-003)     |
| `worker`   | async job worker (queue wiring in a later phase) | startup stub `python -m app.worker` (P0-004) |
| `frontend` | React + Vite empty shell (no product UI)          | runs Vite dev server on 5173 (P0-005) |

Configuration is provided via environment variables. Copy `.env.example` to `.env` and fill
local values. **`.env` is git-ignored; only `.env.example` (placeholders) is committed.**

### Running locally

```bash
cp .env.example .env          # local placeholders only — never real secrets

docker compose config         # validate the Compose file
docker compose build          # build the backend + frontend images (worker reuses backend)
docker compose up -d          # start all local services (postgres, redis, minio, backend, worker, frontend)

# Backend /health check (reachable from the host):
curl http://localhost:8000/health   # -> {"status":"ok","service":"stemspace-backend"}
# Frontend shell check (reachable from the host):
curl http://localhost:5173          # -> HTML shell, <title>StemSpace — Phase 0 frontend shell</title>

# Backend tests (includes the worker startup stub test):
docker compose run --rm --no-deps backend python -m pytest -q
# Worker startup check (exits 0 after printing one safe stub line):
docker compose run --rm --no-deps worker python -m app.worker --check
# Frontend build smoke check:
docker compose run --rm --no-deps frontend npm run build

docker compose logs --tail=20 worker   # -> "[stemspace-worker] Phase 0 worker startup stub ..."
docker compose down           # stop everything
```

`docker compose build` builds only the `backend` and `frontend` images (the `worker` reuses the
backend image; `postgres` / `redis` / `minio` are pulled). The `backend` container serves
`GET /health` via uvicorn; the `worker` container runs the Phase 0 startup stub
(`python -m app.worker`) that prints one safe line and idles; the `frontend` container runs the
Vite dev server for the Phase 0 empty shell, bound to `0.0.0.0:5173` and mapped to the host
`FRONTEND_PORT` (default 5173). The frontend service has **no** `env_file` — the shell needs no
config and must never receive backend/storage secrets or internal service URLs.

> **Behind a TLS-intercepting proxy:** the frontend image's `npm install` fetches from the public
> npm registry. If Docker builds run behind a TLS-intercepting proxy (a corporate TLS proxy), a
> fresh container won't trust the proxy's CA and the install fails. Configure Docker/container CA
> trust **outside the repository**; do **not** disable TLS verification. The committed Dockerfile
> carries no TLS bypass.

## Repository layout

```text
.
├── README.md
├── .env.example          # placeholders only — never real secrets
├── .gitignore
├── .gitattributes
├── .editorconfig
├── docker-compose.yml    # local services: postgres, redis, minio, backend, worker, frontend
├── docs/                 # project documentation and task files
│   ├── README.md
│   ├── coding-rules.md
│   ├── git-workflow.md
│   ├── tasks/phase-0/    # six Phase 0 task docs + phase-0-final-closure-gate.md
│   ├── decisions/        # DEC-0001..0003
│   ├── prd/              # PRD references when supplied
│   ├── architecture/     # architecture/LLD references when supplied
│   └── spike/            # spike results (e.g. AI benchmark evidence)
├── backend/              # FastAPI backend (Phase 0: /health + config only)
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── app/              # main.py (/health) + config.py + worker.py (P0-004 stub)
│   └── tests/            # test_health.py, test_config.py, test_worker_startup.py
├── frontend/             # React + Vite empty shell (Phase 0: no product UI)
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json      # + package-lock.json (react, react-dom, vite)
│   ├── index.html
│   ├── vite.config.js    # dev server bound to 0.0.0.0:5173
│   └── src/              # main.jsx, App.jsx (placeholder), index.css
└── infra/                # local infra assets (later Phase 0 tasks)
```

## Coding rules (summary)

Full rules: `docs/coding-rules.md`. Highlights:

- **Minimal code, no over-engineering** — implement only the current approved task; no future
  abstractions, no duplicate logic (`docs/decisions/DEC-0002`).
- **Private storage only** — no public buckets, no permanent object URLs; the backend grants
  short-lived signed URLs only after authorization (`docs/decisions/DEC-0003`).
- **Frontend** — API calls only through `src/api`; no business logic inside components; no
  messy inline CSS.
- **Backend** — thin routes, focused services, explicit Pydantic schemas.

## Git workflow

Commit conventions (commit after each completed feature/task, right-sized commits and
messages) are documented in `docs/git-workflow.md`.

## Secrets policy

Never commit, request or print real passwords, tokens, client secrets, private keys,
certificates or private connection strings. Use **placeholders only** (`docs/coding-rules.md`).

## Phase 0 does NOT build

To keep scope closed, Phase 0 deliberately does **not** build:

- upload API;
- queue/job processing;
- DB domain models;
- authentication;
- AI model execution / inference;
- billing;
- admin;
- public library;
- public storage;
- resumable upload;
- extra stems beyond Vocals + Background.

## Evidence expectations

Every implementation task returns an evidence report (see
`stemspace-dev-pack-v0.1/templates/evidence-report-template.md`) containing: changed files;
checks/commands run; automated test results; manual verification; deviations; blockers; and a
confirmation that no out-of-scope work was done. Phase 0 closure additionally requires the full
service-startup evidence listed in `docs/tasks/phase-0/phase-0-final-closure-gate.md` (that gate
is **documented, not executed**, until a separate review authorizes running it).
