# Task P2-002 — Domain Models

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

Create minimal SQLAlchemy domain models required by the handoff.

## Context

Models must support future core flow without storing audio bytes in DB.

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

- P2-001 complete.
- Approved entity list.

## Entry Criteria

DB base exists.

## Required Tools

Filesystem write access.

## Forbidden Tools

Routes, services, frontend, worker processing.

## Write Scope

`backend/app/models/` and migration.

## Network / External-System Access

No external network.

## What to Do

- Create models: User, Song, AudioFile, SeparationJob, Tag, SongTag, Rating, Coupon, CouponRedemption, DailyUsage, UsageEvent, SignedUrlGrant, ContentReport, AdminAuditEvent.
- Add fields needed for MVP and future phases, but avoid over-normalization.
- Create initial migration.

## What Not to Do

- Do not store audio bytes in DB.
- Do not expose models as API schemas.
- Do not add unapproved entities.

## Files Likely to Change

- backend/app/models/*.py
- backend/alembic/versions/*.py
- backend/tests/db/test_models.py

## Data / API / State Requirements

State fields should be explicit and reviewable.

## UI Requirements

No UI.

## Business Rules

No behavior beyond data structure.

## Error Handling

N/A.

## Acceptance Criteria

- All required models exist.
- Migration creates tables.
- No audio byte columns.
- Model set remains minimal.

## Required Automated Tests

- Model creation test.
- Migration test.

## Contract / Compatibility Tests

Future schemas and services consume these models; changes must trigger compatibility review.

## Manual Verification

- Inspect generated DB schema.
- Confirm no audio bytes.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- Models and migration exist.
- Tests pass.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
