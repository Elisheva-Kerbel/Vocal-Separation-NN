# P0-003 — Backend Health and Config

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**
Phase: 0 (Dockerized Project Skeleton) · Package: PKG-P0 · Source: `stemspace-dev-pack-v0.1/tasks/phase-0/TASK-P0-003-backend-health-and-config.md`

> This task is **not** authorized yet. It is documented here for Phase 0 completeness. Do not
> implement it until it is the approved task.

## Goal

Add a minimal FastAPI backend that starts inside Docker and exposes a `/health` smoke-test
endpoint, plus a minimal environment config reader.

## Scope

Write scope: `backend/app/main.py`, `backend/app/core/config.py`, backend tests
(`backend/tests/`), `backend/requirements.txt`. No external services beyond local Compose
dependencies.

## What to build

- A minimal FastAPI app.
- A `GET /health` endpoint returning an explicit safe status.
- A minimal config reader for env placeholders.
- A health test (Pytest).

## What NOT to build

- No auth, upload or song routes.
- No connection to AI inference.
- No domain models.
- No extra API routes beyond `/health`.
- **Phase 0 boundary:** no upload API, no queue processing, no DB domain models, no auth, no AI
  model execution, no billing, no admin, no public library, no public storage, no resumable
  upload, no extra stems.

## Acceptance criteria

- The backend container starts.
- `GET /health` returns OK.
- The health test passes.
- No extra API routes exist.

## Required checks / tests

- **Pytest health test is REQUIRED** and must pass.
- Manual call to `/health` from host or container returns the expected status.

## Evidence expected

- Changed files.
- Health test result (passing).
- The `/health` response captured from host or container.
- Deviations, blockers and a confirmation that no out-of-scope work was done.

## Stop gate

Stop after this task. Run only the approved checks. Return changed files, checks, evidence,
deviations and blockers. **Do not continue to P0-004.**
