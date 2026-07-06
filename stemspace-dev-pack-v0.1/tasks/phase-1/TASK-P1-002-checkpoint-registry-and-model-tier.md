# Task P1-002 — Checkpoint Registry and modelTier

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

Implement server-side mapping from modelTier to internal checkpoint reference.

## Context

Client must never provide checkpoint path, filename or free checkpoint id.

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

- P1-001 complete.
- Approved model tiers.

## Entry Criteria

AI module boundaries exist.

## Required Tools

Filesystem write access.

## Forbidden Tools

Client checkpoint paths, external downloads without approval.

## Write Scope

`backend/ai/checkpoint_registry.py`, tests.

## Network / External-System Access

No network.

## What to Do

- Define accepted tiers: Basic and Professional unless approved otherwise.
- Map tiers to internal registry entries.
- Reject raw path-like values.
- Add tests.

## What Not to Do

- Do not expose internal paths to frontend.
- Do not add extra tiers.

## Files Likely to Change

- backend/ai/checkpoint_registry.py
- backend/tests/ai/test_checkpoint_registry.py

## Data / API / State Requirements

Logical tier only.

## UI Requirements

No UI.

## Business Rules

Free/Pro enforcement occurs later; this task only maps modelTier.

## Error Handling

Invalid tier returns safe error.

## Acceptance Criteria

- Valid tiers resolve internally.
- Path-like input rejected.
- No internal path exposed in public result.

## Required Automated Tests

- Checkpoint registry tests.

## Contract / Compatibility Tests

Future API consumers must use `modelTier`, not checkpoint path.

## Manual Verification

- Run tests.
- Inspect output for leaks.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- Tests pass.
- No path leak.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
