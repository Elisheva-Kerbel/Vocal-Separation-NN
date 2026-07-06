# Task P0-004 — Worker Startup Stub

Artifact Type: Task
Task Type: Implementation
Package: PKG-P0
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness PASS before authorized transfer
Execution allowed: No

## Goal

Add a Celery worker bootstrap that starts cleanly without processing real jobs.

## Context

Worker must be part of Docker Compose from the beginning, but Phase 0 must not process audio.

## Approved Decisions

- Compose-first local development is a user requirement where relevant.
- Minimal code, no over-engineering.
- No secrets in chat, repo or task output.
- No out-of-phase features.

## Source References

- `01-project-context.md`
- `02-product-scope-and-do-not-build.md`
- Matching phase and package files.

## Dependencies

- TASK-P0-002 compose service exists.

## Entry Criteria

Backend dependency environment exists.

## Required Tools

Filesystem write access; local tests.

## Forbidden Tools

AI inference, real Celery tasks, DB writes.

## Write Scope

`backend/app/queue/`, `backend/app/workers/` only.

## Network / External-System Access

Redis via local Compose only.

## What to Do

- Create Celery app config.
- Create worker entrypoint/import path.
- Ensure worker container starts.
- Add import/start smoke test if feasible.

## What Not to Do

- Do not create separation task.
- Do not run inference.
- Do not create DB writes.
- Do not implement retries yet.

## Files Likely to Change

- backend/app/queue/celery_app.py
- backend/app/workers/worker.py
- backend/tests/test_worker_import.py

## Data / API / State Requirements

No domain state.

## UI Requirements

No UI.

## Business Rules

N/A.

## Error Handling

Fail clearly if Redis URL missing.

## Acceptance Criteria

- Worker imports.
- Worker container starts.
- No real tasks registered beyond startup stub unless Celery internals require defaults.

## Required Automated Tests

- Worker import test.

## Contract / Compatibility Tests

N/A.

## Manual Verification

- Start worker container.
- Confirm it does not execute product work.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- Worker startup works.
- No processing logic.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
