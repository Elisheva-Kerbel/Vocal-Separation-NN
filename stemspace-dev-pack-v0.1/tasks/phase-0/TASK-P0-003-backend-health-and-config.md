# Task P0-003 — Backend Health and Config

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

Add a minimal FastAPI backend with `/health` and environment config.

## Context

Backend must start inside Docker and expose a smoke-test endpoint only.

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

Backend skeleton and Dockerfile exist.

## Required Tools

Filesystem write access; local tests.

## Forbidden Tools

Auth, DB domain logic, upload routes, AI inference, production credentials.

## Write Scope

`backend/app/main.py`, `backend/app/core/config.py`, backend tests.

## Network / External-System Access

No external services except local Compose dependencies.

## What to Do

- Create minimal FastAPI app.
- Add `/health` endpoint.
- Add minimal config reader for env placeholders.
- Add health test.

## What Not to Do

- Do not add auth/upload/song routes.
- Do not connect to AI inference.
- Do not create domain models.

## Files Likely to Change

- backend/app/main.py
- backend/app/core/config.py
- backend/tests/test_health.py
- backend/requirements.txt

## Data / API / State Requirements

`/health` only.

## UI Requirements

No UI.

## Business Rules

N/A.

## Error Handling

Health endpoint returns explicit safe status.

## Acceptance Criteria

- Backend container starts.
- `GET /health` returns OK.
- Health test passes.
- No extra API routes.

## Required Automated Tests

- Pytest health test.

## Contract / Compatibility Tests

N/A.

## Manual Verification

- Call `/health` from host or container.
- Inspect available routes if practical.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- Health works.
- No business logic.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
