# P0-002 — Docker Compose and Dockerfiles

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**
Phase: 0 (Dockerized Project Skeleton) · Package: PKG-P0 · Source: `stemspace-dev-pack-v0.1/tasks/phase-0/TASK-P0-002-docker-compose-and-dockerfiles.md`

> This task is **not** authorized yet. It is documented here for Phase 0 completeness. Do not
> implement it until it is the approved task.

## Goal

Create the Docker Compose local environment and minimal Dockerfiles so PostgreSQL, Redis,
MinIO, backend, worker and frontend are wired together consistently (Compose-first,
`docs/decisions/DEC-0001`).

## Scope

Write scope: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`,
`backend/.dockerignore`, `frontend/.dockerignore`, `.env.example`. No production deployment
files.

## What to build

- Six Compose services: `postgres`, `redis`, `minio`, `backend`, `worker`, `frontend`.
- Internal URLs use **service names**, not `localhost`.
- Named volumes for PostgreSQL and MinIO local data.
- A backend Dockerfile for the FastAPI environment.
- A frontend Dockerfile for the Vite environment.
- The **worker reuses the backend image / a targeted backend build stage** to avoid duplicated
  dependency definitions.
- `.env.example` with **placeholders only**.

## What NOT to build

- No business logic.
- Do not run migrations automatically.
- No real secrets.
- No production deployment files.
- **Phase 0 boundary:** no upload API, no queue processing, no DB domain models, no auth, no AI
  model execution, no billing, no admin, no public library, no public storage, no resumable
  upload, no extra stems.

## Acceptance criteria

- `docker compose config` is **valid**.
- All six services are defined.
- Backend, worker and frontend have valid build contexts.
- No real secrets (placeholders only).
- The worker reuses the backend dependency definition where practical.

## Required checks / tests

- **Docker Compose config validation is REQUIRED** — `docker compose config` must succeed.
- **Docker build readiness is REQUIRED** — the backend and frontend build contexts must parse
  and be build-ready (Dockerfile parse / build smoke). *(Strengthened from the source's
  "if approved": for Phase 0 readiness this is a required Stop-Gate check, not optional.)*
- Confirm env values are placeholders and internal URLs use Compose service names.

## Evidence expected

- Changed files.
- **Final Docker Compose config/build readiness evidence (REQUIRED):** the output of
  `docker compose config` (valid) and evidence that the backend/frontend build contexts are
  build-ready.
- Manual verification: services inspected, env placeholders confirmed, no production secret
  values.
- Deviations, blockers and a confirmation that no out-of-scope work was done.

## Stop gate

Stop after this task. Run only the approved checks. Return changed files, checks, evidence,
deviations and blockers. **Do not continue to P0-003.**
