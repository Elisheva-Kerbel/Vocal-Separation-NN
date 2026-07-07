# Phase 0 — Final Closure Gate

Status: **Draft — pending readiness review. Not approved for AI code agent execution.**
Phase: 0 (Dockerized Project Skeleton) · Package: PKG-P0
Source: `stemspace-dev-pack-v0.1/phases/PHASE-00-dockerized-project-skeleton.md`,
`stemspace-dev-pack-v0.1/packages/PKG-P0-dockerized-project-skeleton.md`,
`stemspace-dev-pack-v0.1/07-testing-and-evidence-strategy.md`.

> **Documented, not executed.** This gate is written down here so the closure requirements are
> unambiguous. It is **not** run as part of any individual task (including P0-006). It is executed
> only when a separate review **explicitly authorizes Phase 0 closure**. Do not run it as a
> substitute for review.

## Purpose

Prove that the Phase 0 dockerized skeleton starts and behaves as a **local development skeleton
only** — before any work moves beyond Phase 0. Passing this gate does **not** grant approval for
production, public users, upload processing, or any later phase.

## Scope reminder — what Phase 0 is (and is not)

Phase 0 provides: a Docker Compose local skeleton; a backend FastAPI `GET /health`; a worker
**startup stub**; a frontend Phase 0 **empty shell**; and PostgreSQL, Redis and MinIO as **local
infrastructure services only**. It contains **no product flow**.

Phase 0 explicitly does **not** include: upload API; queue/job processing; DB/domain models;
auth; AI model execution; billing; admin; public library; public storage; resumable upload;
extra stems; or any product workflow.

## Closure checklist — ALL must pass

Run from a clean checkout with `cp .env.example .env` (local placeholders only):

1. **`docker compose config`** is valid (exit 0).
2. **`docker compose build`** builds the backend and frontend images successfully.
3. **`docker compose up --build`** starts all local services.
4. **Backend `/health` reachable from the host** — `curl http://localhost:8000/health` returns
   `{"status":"ok","service":"stemspace-backend"}`.
5. **Frontend loads from the host** — `curl http://localhost:5173` returns the Phase 0 shell HTML
   (`<title>StemSpace — Phase 0 frontend shell</title>`).
6. **Worker starts and logs the safe stub message** — the worker container prints the Phase 0
   startup-stub line and idles (no queue, no connections).
7. **PostgreSQL service starts** (as local infrastructure only; reachable by Compose service name).
8. **Redis service starts** (as local infrastructure only; reachable by Compose service name).
9. **MinIO service starts** (as local infrastructure only; reachable by Compose service name).
10. **Backend tests pass** — `docker compose run --rm --no-deps backend python -m pytest -q`.
11. **Worker startup check passes** — `docker compose run --rm --no-deps worker python -m app.worker --check` exits 0.
12. **Frontend build passes** — `docker compose run --rm --no-deps frontend npm run build`.
13. **No secrets exposed** — only `.env.example` placeholders are committed; no real credentials,
    keys, certificates, or private connection strings anywhere in the repo or rendered output; the
    frontend receives no backend/storage secrets or internal service URLs.
14. **Dev Pack untouched** — `git status --short -- stemspace-dev-pack-v0.1` is empty.
15. **Git status clean after commit** — `git status --short` is clean once the approved changes
    are committed.

Tear down with `docker compose down` after the gate.

## Environment note (generic)

If Docker builds run behind a **TLS-intercepting proxy** (a corporate TLS proxy), configure
Docker/container CA trust **outside the repository** and keep TLS verification on. Do not commit
TLS-bypass flags, private certificates, CA paths, or provider-specific proxy configuration.

## Not production

Phase 0 is a local development skeleton only. It is **not** approved for production, **not**
approved for public users, and **not** approved for upload processing. **Phase 1 is the AI
Benchmark Harness only** and must remain isolated until it is explicitly approved.

## Evidence on closure

When the gate is authorized and run, capture: command outputs for checks 1–15; confirmation that
status/labels remain accurate and no false approval is implied; deviations; blockers; and a
confirmation that no out-of-scope work was performed.
