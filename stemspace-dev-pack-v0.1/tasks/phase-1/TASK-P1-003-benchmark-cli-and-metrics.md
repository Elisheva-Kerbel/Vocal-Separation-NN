# Task P1-003 — Benchmark CLI and Metrics

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

Create benchmark CLI that writes outputs and metrics JSON.

## Context

Benchmark must run before Upload API/Queue integration.

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

- P1-001 and P1-002 complete.
- Model availability or stub explicitly accepted for skeleton only.

## Entry Criteria

AI modules exist.

## Required Tools

Filesystem write access.

## Forbidden Tools

Upload API, DB, Celery, production storage.

## Write Scope

`backend/scripts/run_benchmark.py`, `backend/ai/metrics.py`, tests.

## Network / External-System Access

No production network. Model file access only if approved.

## What to Do

- Add CLI arguments: input audio path, output directory, modelTier.
- Call inference flow.
- Write vocals/background outputs on success.
- Write metrics JSON.
- Capture success/failure/failure reason.

## What Not to Do

- Do not connect to API/queue.
- Do not accept checkpoint path.
- Do not commit generated audio outputs.

## Files Likely to Change

- backend/scripts/run_benchmark.py
- backend/ai/inference.py
- backend/ai/metrics.py
- backend/tests/ai/test_metrics_shape.py

## Data / API / State Requirements

Metrics schema stable.

## UI Requirements

No UI.

## Business Rules

Vocals + Background only.

## Error Handling

On failure, write/return failure reason without stack trace leaking secrets.

## Acceptance Criteria

- CLI accepts modelTier.
- Metrics include total_runtime, decode_time, inference_time, encode_time, output_sizes, success/failure, failure_reason, checkpoint cold/warm if possible.
- Generated outputs ignored by Git.

## Required Automated Tests

- Metrics schema test.
- CLI argument validation test if feasible.

## Contract / Compatibility Tests

N/A.

## Manual Verification

- Run CLI on small fixture if available.
- Inspect metrics JSON.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- CLI and metrics work.
- No out-of-scope integration.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
