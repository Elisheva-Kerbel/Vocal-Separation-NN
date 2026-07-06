# StemSpace — Vocal Removing Platform

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**
Source of truth: `stemspace-dev-pack-v0.1/` (STEMSPACE-DEV-PACK-001 v0.1).

## Purpose

StemSpace is a platform where a user can log in, upload audio, process it asynchronously into
**Vocals + Background**, and securely listen to / download the outputs via short-lived signed
URLs. Files are private; the backend authorizes every access.

This repository is being built in **small, testable phases**. It is **not** built in one pass.

## Current phase

**Phase 0 — Dockerized Project Skeleton.** Phase 0 creates a minimal monorepo foundation that
can eventually start via Docker Compose, with documentation and Git baseline files, and **no
business logic**. See `docs/tasks/phase-0/` for the per-task documents.

So far, **TASK-P0-001** (skeleton, docs and Git baseline), **TASK-P0-002** (Docker Compose,
Dockerfiles and `.env.example`), **TASK-P0-003** (backend `/health` and config), **TASK-P0-004**
(worker startup stub) and **TASK-P0-005** (frontend empty shell) have been performed. The backend
serves a minimal `GET /health` smoke endpoint, the worker container runs a minimal **startup
stub** (`python -m app.worker`), and the frontend container now runs the **Vite + React empty
shell** (`frontend/src/App.jsx`) — a static Phase 0 placeholder that makes **no** backend API
calls, stores no files/tokens/secrets and implements **no** product flow. There is still **no
queue/job processing** and **no product UI**.

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
docker compose build backend  # build the backend image (worker reuses it)
docker compose run --rm backend python -m pytest   # run backend tests (incl. worker stub)
docker compose run --rm --no-deps worker python -m app.worker --check   # worker startup smoke check -> exits 0
docker compose up -d backend  # start the FastAPI backend (with postgres/redis/minio)
curl http://localhost:8000/health   # -> {"status":"ok","service":"stemspace-backend"}
docker compose up -d worker   # start the worker startup stub (prints one line, idles)
docker compose logs --tail=20 worker   # -> "[stemspace-worker] Phase 0 worker startup stub ..."
docker compose build frontend # build the frontend empty-shell image
docker compose up -d --no-deps frontend   # start the Vite dev server (0.0.0.0:5173)
curl http://localhost:5173    # -> HTML shell, <title>StemSpace — Phase 0 frontend shell</title>
docker compose down           # stop everything
```

The `worker` service reuses the backend image, so only `backend` and `frontend` are built.
The `backend` container serves `GET /health` via uvicorn; the `worker` container runs the
Phase 0 startup stub (`python -m app.worker`) that prints one safe line and idles; the
`frontend` container runs the Vite dev server for the Phase 0 empty shell, bound to
`0.0.0.0:5173` and mapped to the host `FRONTEND_PORT` (default 5173). The frontend service has
**no** `env_file` — the shell needs no config and must never receive backend/storage secrets or
internal service URLs.

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
│   ├── tasks/phase-0/    # six Phase 0 task documents
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
service-startup evidence listed in `docs/tasks/phase-0/P0-006-readme-and-coding-rules.md`.
