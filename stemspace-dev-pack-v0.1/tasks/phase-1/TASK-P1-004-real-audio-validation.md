# Task P1-004 — Real Audio Benchmark Validation

Artifact Type: Task
Task Type: Validation
Package: PKG-P1
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness PASS before authorized transfer
Execution allowed: No

## Goal

Validate benchmark harness with one real audio file and return evidence.

## Context

This is validation only. It must not modify code.

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

- P1-003 complete.
- Real local audio fixture available.
- Nadav approved validation task.

## Entry Criteria

Benchmark CLI exists.

## Required Tools

Read/execute access to local benchmark environment.

## Forbidden Tools

Code edits, API integration, queue integration, production storage.

## Write Scope

No write scope except benchmark output directory and evidence report.

## Network / External-System Access

No external network unless model access was separately approved.

## What to Do

- Run benchmark on one real audio file.
- Collect outputs.
- Collect metrics JSON.
- Record failure if validation fails.

## What Not to Do

- Do not fix code.
- Do not alter model choices.
- Do not connect to upload API.

## Files Likely to Change

- evidence/benchmark/* only, if evidence path is part of repo; otherwise external evidence report.

## Data / API / State Requirements

No API state.

## UI Requirements

No UI.

## Business Rules

N/A.

## Error Handling

Report safe failure reason.

## Acceptance Criteria

- Vocals output exists.
- Background output exists.
- Metrics JSON exists.
- modelTier accepted.
- No checkpoint path supplied.

## Required Automated Tests

- No new tests; this is manual validation.

## Contract / Compatibility Tests

N/A.

## Manual Verification

- Inspect output files.
- Inspect metrics JSON.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- Validation evidence returned.
- No code changes.
- Blockers documented if failed.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
