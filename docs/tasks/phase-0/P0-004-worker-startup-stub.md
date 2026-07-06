# P0-004 — Worker Startup Stub

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**
Phase: 0 (Dockerized Project Skeleton) · Package: PKG-P0 · Source: `stemspace-dev-pack-v0.1/tasks/phase-0/TASK-P0-004-worker-startup-stub.md`

> This task is **not** authorized yet. It is documented here for Phase 0 completeness. Do not
> implement it until it is the approved task.

## Goal

Add a Celery worker bootstrap that starts cleanly **without processing real jobs**. The worker
is part of Docker Compose from the beginning, but Phase 0 processes no audio.

## Scope

Write scope: `backend/app/queue/`, `backend/app/workers/` only. Redis via local Compose only.

## What to build

- A Celery app config (`backend/app/queue/celery_app.py`).
- A worker entrypoint / import path (`backend/app/workers/worker.py`).
- A worker that imports and whose container starts cleanly.
- A worker import/start smoke test (`backend/tests/test_worker_import.py`).

## What NOT to build

- No separation task, no AI inference.
- No DB writes.
- No retries yet.
- No real tasks registered beyond what is required for startup (unless Celery internals require
  defaults).
- **Phase 0 boundary:** no upload API, no queue processing, no DB domain models, no auth, no AI
  model execution, no billing, no admin, no public library, no public storage, no resumable
  upload, no extra stems.

## Acceptance criteria

- The worker imports.
- The worker container starts.
- No real tasks are registered beyond the startup stub (unless Celery internals require
  defaults).

## Required checks / tests

- **Worker import/start smoke check is REQUIRED** — the worker import test must pass and the
  worker must start cleanly. *(Strengthened from the source's "if feasible": this smoke check
  is a required Phase 0 readiness Stop-Gate check, aligned with the source's already-required
  worker import test.)*
- Fail clearly if the Redis URL is missing.

## Evidence expected

- Changed files.
- Worker import/start smoke check result (passing) and evidence the worker container starts
  without executing product work.
- Deviations, blockers and a confirmation that no out-of-scope work was done.

## Stop gate

Stop after this task. Run only the approved checks. Return changed files, checks, evidence,
deviations and blockers. **Do not continue to P0-005.**
