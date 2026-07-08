# P1-004A — Basic Local Model Decision Record

Status: **Authorized (docs-only) — decision record for the Basic local model prototype.**
Phase: 1 (AI Benchmark Harness) · Package: PKG-P1 · Records: `docs/decisions/DEC-0004-basic-local-model-prototype.md`
Source: user-approved decisions + `stemspace-dev-pack-v0.1/tasks/phase-1/TASK-P1-004-real-audio-validation.md` (baseline)

> This task is **documentation / planning only**. It authorizes **no** inference, **no** runtime code, **no**
> dependency installation, **no** model download or checkpoint copy, and **no** system integration. It captures
> the approved decision to use a Basic local model prototype and defines the safe next implementation step.

## Goal

Produce and record the approved decision (**DEC-0004**) that the locally available, self-trained checkpoint may be
used as a **Basic local prototype only**, and define the safe sequencing (P1-004B, then P1-004C) for any future
implementation.

## Scope

Docs-only. Write scope is limited to:

- `docs/decisions/DEC-0004-basic-local-model-prototype.md`
- `docs/tasks/phase-1/P1-004A-basic-local-model-decision-record.md` (this file)
- `docs/tasks/phase-1/P1-004B-minimal-local-inference-adapter.md` (planning stub)
- `docs/tasks/phase-1/P1-004C-real-audio-validation.md` (planning stub)

No network access. No changes to `backend/`, benchmark CLI, Dockerfiles, `requirements.txt`, `docker-compose.yml`,
`frontend/`, or `stemspace-dev-pack-v0.1/`.

## What to build

- **DEC-0004** decision record capturing all approved user decisions:
  - Basic local model prototype only; local prototype / technical validation only.
  - Approved checkpoint source is the **local out-of-band folder only** (not committed).
  - Checkpoint / model weights **must not** be committed to Git now or ever.
  - Internal `use_best_model` selector behavior (server-side), with the Basic slot temporarily allowed to reuse the
    same checkpoint — **explicitly not** a Professional tier.
  - Professional remains **not implemented / blocked** pending a separate production-grade checkpoint.
  - No production / commercial approval for the current checkpoint; licensing / provenance still to be resolved.
  - Expected future dependencies documented **without installing** them.
  - Checkpoint-loading security notes (pickle risk, safe loading, no path exposure).
  - Task sequencing P1-004A → P1-004B → P1-004C.
- This P1-004A task doc.
- P1-004B and P1-004C **planning stubs** clearly marked "not authorized yet."

## What NOT to build

- No inference, no model loading into memory, no real audio validation run.
- No runtime code; no edits to `backend/ai/*`, `backend/scripts/*`, `backend/tests/*`.
- No dependency installation; no edit to `backend/requirements.txt`.
- No Dockerfile / `docker-compose.yml` changes.
- No checkpoint / model / audio files copied into the repo.
- No connection to API, DB, queue, Redis, MinIO/S3, frontend or worker.
- No claim of production readiness, commercial approval, or Professional implementation.
- No start of Phase 2.

## Acceptance criteria

1. `DEC-0004` exists and captures **all** approved user decisions.
2. `DEC-0004` states **local prototype / technical validation only**.
3. `DEC-0004` states **no production / commercial approval** for the current checkpoint.
4. `DEC-0004` states checkpoint / model weights **must not be committed to Git**.
5. `DEC-0004` documents `use_best_model` behavior **without** presenting Professional as implemented.
6. `DEC-0004` documents **expected dependencies without installing** them.
7. This task doc has Goal, Scope, What to build, What not to build, Acceptance criteria, Evidence, Stop gate.
8. **No runtime code** is modified.
9. **No dependencies** are installed.
10. **No checkpoint / model / audio files** are copied into the repo.
11. **No inference** or real audio validation is run.
12. Source Dev Pack (`stemspace-dev-pack-v0.1/`) is **not modified**.
13. Task **stops** after P1-004A.

## Evidence expected

- List of files created / changed (docs-only).
- `git status --short` showing only docs under allowed scope.
- Checkpoint / model / audio file scan result (excluding the Dev Pack): none added.
- `git status --short -- stemspace-dev-pack-v0.1` showing the Dev Pack unchanged.
- Confirmation that no runtime code changed, no dependencies installed, no inference run.
- Deviations, blockers and remaining risks.

## Stop gate

Stop after P1-004A. Do not implement P1-004B. Do not run inference. Do not install dependencies. Wait for review.
