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

At the time of writing, only **TASK-P0-001** (this skeleton, docs and Git baseline) has been
performed. Docker Compose, Dockerfiles, backend, worker and frontend code are **later Phase 0
tasks** and are not yet implemented.

## Planned local development (Compose-first)

Local development is **Docker Compose-first** (see `docs/decisions/DEC-0001`). Once the later
Phase 0 tasks are approved and implemented, `docker compose up` will start these services,
wired by **service name** (not `localhost`):

| Service    | Role                                             |
|------------|--------------------------------------------------|
| `postgres` | PostgreSQL database                              |
| `redis`    | Redis broker/result backend for Celery           |
| `minio`    | S3-compatible private object storage (local dev) |
| `backend`  | FastAPI app (Phase 0 exposes only `/health`)     |
| `worker`   | Celery worker (Phase 0: startup stub only)       |
| `frontend` | React + Vite shell (Phase 0: empty shell)        |

Configuration is provided via environment variables. Copy `.env.example` to `.env` and fill
local values. **`.env` is git-ignored; only `.env.example` (placeholders) is committed.**

## Repository layout

```text
.
├── README.md
├── .env.example          # placeholders only — never real secrets
├── .gitignore
├── .gitattributes
├── .editorconfig
├── docs/                 # project documentation and task files
│   ├── README.md
│   ├── coding-rules.md
│   ├── git-workflow.md
│   ├── tasks/phase-0/    # six Phase 0 task documents
│   ├── decisions/        # DEC-0001..0003
│   ├── prd/              # PRD references when supplied
│   ├── architecture/     # architecture/LLD references when supplied
│   └── spike/            # spike results (e.g. AI benchmark evidence)
├── backend/              # backend app (later Phase 0 tasks)
├── frontend/             # frontend app (later Phase 0 tasks)
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
