# Task P2-004 — Seed Tags and DB Tests

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

Add a minimal seed script for tags and core DB tests.

## Context

Tags support library/public features later, but only seed foundation is needed now.

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

Tag model exists.

## Required Tools

Filesystem write access; local DB.

## Forbidden Tools

Frontend, public library, admin moderation.

## Write Scope

`backend/scripts/seed_tags.py`, DB tests.

## Network / External-System Access

Local Compose Postgres only.

## What to Do

- Create idempotent seed script for approved default tags.
- Add tests for seed idempotency if feasible.
- Add DB tests for constraints relevant to usage success.

## What Not to Do

- Do not build tag UI.
- Do not build public library.
- Do not add unapproved tag taxonomy if not supplied; use placeholder/minimal seed or mark blocker.

## Files Likely to Change

- backend/scripts/seed_tags.py
- backend/tests/db/test_seed_tags.py
- backend/tests/db/test_usage_event_constraints.py

## Data / API / State Requirements

UsageEvent should support unique successful processing by song.

## UI Requirements

No UI.

## Business Rules

No product taxonomy decision beyond supplied/placeholder tags.

## Error Handling

Safe duplicate seed behavior.

## Acceptance Criteria

- Seed script is idempotent.
- Tests pass.
- UsageEvent uniqueness support is test-covered or blocker documented.

## Required Automated Tests

- Seed test.
- UsageEvent constraint test.

## Contract / Compatibility Tests

Future quota finalization depends on UsageEvent uniqueness evidence.

## Manual Verification

- Run seed twice locally if approved.
- Run tests.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- Seed/test foundation complete.
- No UI or routes.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
