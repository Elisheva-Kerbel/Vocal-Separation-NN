# FAST-DEMO-003 — Backend Demo Slice

Status: **PLANNING STUB — NOT AUTHORIZED YET. Requires an explicit Nadav prompt. Do not implement yet.**
Track: FAST-DEMO (local demo vertical slice) · Package: none
Depends on: FAST-DEMO-002 (read-only `/models` mount + in-container Basic inference proof) — accepted ·
**`docs/decisions/DEC-0009-local-demo-vertical-slice.md`** (the contract for this task)
Relates to: `DEC-0002`, `DEC-0003`, `DEC-0004`, `DEC-0006`, `DEC-0007`, `docs/coding-rules.md`

> **Do not implement yet.** This document is a planning stub. It records *what this task will be* so the
> work can start mechanically when authorized — it authorizes **nothing** on its own. No route, no
> module, no test and no commit may be produced until Nadav issues an explicit FAST-DEMO-003
> implementation prompt. When that prompt arrives, implement **exactly** the DEC-0009 contract; the code
> agent must not re-decide any of it (`docs/coding-rules.md` §9).

## Goal

Add the smallest backend surface that turns the already-proven Basic local separation into something a
browser can call: **two routes under `/demo`**, synchronous processing, local ephemeral storage, safe
failures — and nothing else.

## Contract (fixed by DEC-0009 — do not re-decide)

- **Routes** — exactly `POST /demo/separate` and `GET /demo/jobs/{jobId}/stems/{stem}` (DEC-0009 §5).
  No status/polling route. No route outside the `/demo` prefix.
- **Processing** — synchronous, in-request, Basic tier fixed server-side (DEC-0009 §3 D1, §5).
- **Storage** — local temp folder under `DEMO_DATA_DIR`, per-job UUID subdirectory, ephemeral
  (DEC-0009 §7).
- **Input** — 20 MB default byte cap enforced before buffering; MP3 and WAV both accepted; **prefer the
  raw request body** over `UploadFile` so no `python-multipart` dependency is added (DEC-0009 §8).
- **Reuse, do not modify** — `backend/ai/*` and `backend/scripts/run_benchmark.py` are used as-is.

## What to build (when authorized)

- One **flat module** under `backend/app/` holding the two routes plus their local-disk handling and
  safe error mapping, wired into `app/main.py`.
- Any response model defined **inside that module**.
- Tests covering DEC-0009 §9.1–§9.5.

## What NOT to build

- No `app/api/`, `app/routers/` or `app/services/` directory — an existing P2-003 test asserts their
  absence.
- No new class in `app/schemas/` — its class set is closed by `DEC-0007` and asserted by a test.
- No auth, queue, Celery, Redis, worker change, MinIO/S3, storage client, signed URL, DB read or write,
  Alembic run, billing, admin, library, Professional tier or extra stem.
- No `StaticFiles` mount, no directory listing, no public or permanent URL.
- No new pip dependency (see DEC-0009 §8), no image rebuild driven by `requirements.txt`.
- No change to `/health`, the worker, the frontend, the DB models/schemas/migrations or the Dev Pack.

## Security rules (binding)

- `jobId` is an **opaque UUID**, validated before use; `stem` is limited to `vocals` | `background`.
- Filesystem paths are composed **server-side** only — **no client input may become a path segment**.
- No response, error, log or metric may contain a host path, `/models`, a checkpoint path or filename,
  `LOCAL_MODEL_ROOT`, `storage_key` or any secret (DEC-0009 §4).
- Failures use **fixed coded reasons** in the existing `scripts/run_benchmark.py` style — never a
  traceback and never an echo of client input.

## Files likely to change

- `backend/app/main.py` — mount the demo routes.
- `backend/app/<demo module>.py` — **new**.
- `backend/tests/test_demo_*.py` — **new**.
- `backend/tests/test_health.py` — deliberately re-scope `test_no_out_of_scope_routes` to allow
  `/demo/*` while still forbidding `/auth`, `/login`, `/songs`, `/library`, `/admin`. Do not delete or
  otherwise weaken it.

## Required checks (when authorized)

1. `docker compose run --rm --no-deps backend python -m pytest -q` — full suite green, including the
   Phase 0/1/2 regressions.
2. New demo tests: happy path (**inference mocked**), safe failure, invalid stem / unknown job, no
   path/secret leak, no `storage_key` leak.
3. `docker compose config` still valid; `git status --short` shows only in-scope files.
4. No model / checkpoint / audio file added to the repo.

## Evidence to return

Changed files · checks and tests run · deviations · blockers · confirmation that no out-of-scope work was
done and that no path, secret, checkpoint reference or `storage_key` is exposed.

## Stop gate

Stop after this task. Do not start FAST-DEMO-004. Return the evidence report and wait for review.
