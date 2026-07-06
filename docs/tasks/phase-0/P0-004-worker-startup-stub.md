# P0-004 — Worker Startup Stub

Status: **Implemented — functionally accepted in the P0-004 closeout review.**
Phase: 0 (Dockerized Project Skeleton) · Package: PKG-P0 · Source: `stemspace-dev-pack-v0.1/tasks/phase-0/TASK-P0-004-worker-startup-stub.md`

> This document is the **active implementation contract** for P0-004 after the closeout review.
> It describes the **approved implementation**, which deliberately deviates from the source Dev
> Pack task (see **Deviation from source** below). The Dev Pack is read-only historical source.

## Goal

Add a minimal **worker startup stub** that proves the `worker` service can import project code
and start cleanly under Docker Compose — with **no queue framework**, **no broker**, **no
connections** and **no job processing**. Phase 0 processes no audio.

## Scope

Write scope: `backend/app/worker.py` and `backend/tests/test_worker_startup.py`. The `worker`
Compose service reuses the backend image (no separate build). No external services and no
network / connection access.

## What to build

- A worker module `backend/app/worker.py` exposing a `python -m app.worker` entrypoint that:
  - `python -m app.worker --check` — runs a **startup smoke check**: prints one safe line (no
    secret, no connection string) and exits 0. Used by the tests and the Compose one-shot check.
  - `python -m app.worker` — long-running stub: prints one safe line and then idles to keep the
    container alive, with **no** polling loop and **no** queue client.
- The Compose `worker` service runs `python -m app.worker`, **reusing the backend image**
  (`stemspace-backend:local`) — no separate worker image/build.
- A worker startup/import smoke test `backend/tests/test_worker_startup.py`.

## What NOT to build

- **No Celery, no RQ, no Dramatiq** — no task / queue / broker framework of any kind.
- **No Redis client** and no broker / result-backend wiring.
- **No PostgreSQL connection** and no DB client.
- **No MinIO / S3 connection** and no storage client.
- No queue consumption, no job enqueueing.
- No audio processing, no AI inference, no business logic.
- No reading or printing of any secret or connection string.
- **Phase 0 boundary:** no upload API, no queue processing, no DB domain models, no auth, no AI
  model execution, no billing, no admin, no public library, no public storage, no resumable
  upload, no extra stems.

## Acceptance criteria

- The worker module imports and exposes a callable entrypoint.
- `python -m app.worker --check` runs and exits 0, printing one safe startup line.
- The `worker` container starts (reusing the backend image) and idles without executing product
  work and without opening any connection.
- No queue / broker client (Celery, Redis, RQ, Dramatiq) is installed or imported.

## Required checks / tests

- **Worker startup/import smoke check is REQUIRED — not optional.** The worker module must
  import and `python -m app.worker --check` must exit 0. This is a required Phase 0 readiness
  Stop-Gate check. *(Strengthened from the source's "add import/start smoke test if feasible".)*
- The startup-stub tests (`backend/tests/test_worker_startup.py`) must pass: module import,
  `--check` exits 0, the startup output leaks no secret / connection string, and no queue-client
  dependency (Celery, Redis, RQ, Dramatiq) is installed.

## Deviation from source

The source Dev Pack task (`TASK-P0-004`) sketched a **Celery** bootstrap under
`backend/app/queue/` and `backend/app/workers/`, with a Redis URL and a "fail clearly if Redis
URL missing" check. The approved implementation is a **no-broker startup stub** instead:
`backend/app/worker.py` with no Celery / Redis, opening no connections. Because the stub imports
no Redis client and holds no connection string, the source's Redis-URL error check does not
apply. Real queue wiring (Celery broker, tasks, consumption) is deferred to a later, separately
approved phase.

## Evidence expected

- Changed files.
- Worker startup/import smoke check result (passing) and evidence the `worker` container starts
  and idles without executing product work.
- Deviations, blockers and a confirmation that no out-of-scope work was done.

## Stop gate

Stop after this task. Run only the approved checks. Return changed files, checks, evidence,
deviations and blockers. **Do not continue to P0-005.**
