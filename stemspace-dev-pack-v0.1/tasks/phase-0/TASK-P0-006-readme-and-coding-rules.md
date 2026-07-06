# Task P0-006 — README and Coding Rules

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

Document local development, coding rules and scope boundaries for Phase 0.

## Context

Developers and AI agents need clear local run, boundaries and evidence expectations.

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

- Phase 0 files exist or are planned.

## Entry Criteria

Repo skeleton exists.

## Required Tools

Filesystem write access.

## Forbidden Tools

Execution instructions for unapproved AI transfer, secrets, production deployment docs.

## Write Scope

`README.md`, `docs/decisions/`, `docs/coding-rules.md`.

## Network / External-System Access

No network.

## What to Do

- Document project purpose.
- Document local Docker Compose service overview.
- Document no-secrets policy.
- Document minimal-code rule.
- Document what Phase 0 does not build.
- Document evidence expected from implementation tasks.

## What Not to Do

- Do not document unapproved production deployment.
- Do not include real credentials.
- Do not imply Nadav approval.

## Files Likely to Change

- README.md
- docs/coding-rules.md
- docs/decisions/DEC-0001-compose-first-local-dev.md
- docs/decisions/DEC-0002-minimal-code-no-overengineering.md

## Data / API / State Requirements

No API state.

## UI Requirements

No UI.

## Business Rules

No product behavior changes.

## Error Handling

N/A.

## Acceptance Criteria

- README is clear.
- Coding rules exist.
- Docs do not include secrets.
- Status remains Draft until Nadav PASS.

## Required Automated Tests

- Markdown link/readability check if available.

## Contract / Compatibility Tests

N/A.

## Manual Verification

- Open docs.
- Confirm no execution authorization is implied.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- Docs complete.
- No false approval claims.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
