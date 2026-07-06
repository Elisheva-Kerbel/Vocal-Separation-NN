# Task P2-003 — Pydantic Schemas and No Storage Key Leak

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

Create external API schemas that do not expose internal storage keys.

## Context

DB models are not API schemas. Frontend must never receive storage key.

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

- P2-002 complete.

## Entry Criteria

Models exist.

## Required Tools

Filesystem write access.

## Forbidden Tools

API endpoints beyond schema tests.

## Write Scope

`backend/app/schemas/`, schema tests.

## Network / External-System Access

No external network.

## What to Do

- Create minimal schemas for user, song, job and common responses.
- Exclude `storage_key` and internal file refs from external schemas.
- Add tests proving no storage key serialization.

## What Not to Do

- Do not add routes.
- Do not expose DB models directly.
- Do not leak storage refs.

## Files Likely to Change

- backend/app/schemas/user.py
- backend/app/schemas/song.py
- backend/app/schemas/job.py
- backend/app/schemas/common.py
- backend/tests/schemas/test_no_storage_key_leak.py

## Data / API / State Requirements

External schema shape only.

## UI Requirements

No UI.

## Business Rules

Private storage rule.

## Error Handling

Safe validation errors.

## Acceptance Criteria

- Schemas exist.
- storage_key is absent from serialized schema output.
- Internal fields remain internal.

## Required Automated Tests

- Schema serialization leak test.

## Contract / Compatibility Tests

Future API providers must pass this test before downstream UI consumes the API.

## Manual Verification

- Inspect schema output.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- No leak tests pass.
- No routes added.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
