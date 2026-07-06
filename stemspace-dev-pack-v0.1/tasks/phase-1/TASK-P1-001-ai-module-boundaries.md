# Task P1-001 — AI Module Boundaries

Artifact Type: Task
Task Type: Implementation
Package: PKG-P1
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness PASS before authorized transfer
Execution allowed: No

## Goal

Create minimal AI module files without connecting to API, DB or queue.

## Context

Phase 1 validates inference outside the application flow.

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

- P0 available.
- Nadav approval for this task.

## Entry Criteria

Backend folder exists.

## Required Tools

Filesystem write access.

## Forbidden Tools

API routes, DB writes, Celery worker tasks, model download scripts unless approved.

## Write Scope

`backend/ai/` and `backend/tests/ai/` only.

## Network / External-System Access

No external model download unless explicitly approved.

## What to Do

- Create `model.py`, `inference.py`, `audio_io.py`, `metrics.py`, `checkpoint_registry.py`, `checkpoints/.gitkeep`.
- Define minimal interfaces only needed for benchmark.
- Add module import tests.

## What Not to Do

- Do not implement upload integration.
- Do not expose checkpoint path.
- Do not add extra stems.

## Files Likely to Change

- backend/ai/model.py
- backend/ai/inference.py
- backend/ai/audio_io.py
- backend/ai/metrics.py
- backend/ai/checkpoint_registry.py
- backend/ai/checkpoints/.gitkeep
- backend/tests/ai/test_imports.py

## Data / API / State Requirements

`modelTier` is logical input for later tasks.

## UI Requirements

No UI.

## Business Rules

Vocals + Background only.

## Error Handling

Return structured failure reasons from benchmark-level functions.

## Acceptance Criteria

- AI modules import.
- No API/DB/queue imports required.
- No checkpoint path accepted from client-style boundary.

## Required Automated Tests

- Import tests.

## Contract / Compatibility Tests

N/A.

## Manual Verification

- Inspect module boundaries.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- Boundaries exist.
- No out-of-scope integration.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
