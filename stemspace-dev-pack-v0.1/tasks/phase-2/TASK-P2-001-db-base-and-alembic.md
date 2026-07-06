# Task P2-001 — DB Base and Alembic

Artifact Type: Task
Task Type: Implementation
Package: PKG-P2
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness PASS before authorized transfer
Execution allowed: No

## Goal

Create SQLAlchemy DB base/session and Alembic migration foundation.

## Context

Domain modeling must be migration-based and safe for local Postgres.

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

- P0 complete.
- Nadav approval for Phase 2 task.

## Entry Criteria

Backend skeleton and Postgres service exist.

## Required Tools

Filesystem write access; local Postgres.

## Forbidden Tools

Production DB, destructive migrations, auth/upload routes.

## Write Scope

`backend/app/db/`, `backend/alembic.ini`, `backend/alembic/`.

## Network / External-System Access

Local Compose Postgres only.

## What to Do

- Create DB base.
- Create session config.
- Create Alembic config/env.
- Add migration test scaffold.

## What Not to Do

- Do not create business endpoints.
- Do not auto-run migrations on app startup.
- Do not connect to production DB.

## Files Likely to Change

- backend/alembic.ini
- backend/alembic/env.py
- backend/alembic/versions/.gitkeep
- backend/app/db/base.py
- backend/app/db/session.py
- backend/tests/db/test_migrations.py

## Data / API / State Requirements

DB URL from env placeholder.

## UI Requirements

No UI.

## Business Rules

N/A.

## Error Handling

Fail clearly on missing DB URL.

## Acceptance Criteria

- Alembic env loads.
- Migration command can target local DB.
- No production DB config.

## Required Automated Tests

- Migration scaffold test.

## Contract / Compatibility Tests

N/A.

## Manual Verification

- Run alembic current/upgrade on empty local DB if approved.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- DB base exists.
- No production risk.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
