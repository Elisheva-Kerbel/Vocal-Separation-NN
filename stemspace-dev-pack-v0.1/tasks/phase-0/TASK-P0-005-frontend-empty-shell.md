# Task P0-005 — Frontend Empty Shell

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

Create a minimal React + Vite frontend shell with approved folder structure.

## Context

Frontend should load but must not build real pages beyond skeleton.

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

- TASK-P0-001 folder structure.
- TASK-P0-002 frontend Dockerfile/compose service.

## Entry Criteria

Frontend folder exists.

## Required Tools

Filesystem write access; local frontend package install/build if approved.

## Forbidden Tools

Backend business calls, auth/upload pages, inline CSS mess.

## Write Scope

`frontend/package.json`, `frontend/src/` skeleton.

## Network / External-System Access

No external API calls except later approved backend health check if explicitly scoped.

## What to Do

- Create Vite React app shell.
- Create approved `src` folders.
- Add empty or placeholder App with no business logic.
- Prepare `src/api` folder for future calls.

## What Not to Do

- Do not build upload/result/public/admin pages.
- Do not add business logic inside JSX.
- Do not duplicate API logic.

## Files Likely to Change

- frontend/package.json
- frontend/src/main.jsx
- frontend/src/App.jsx
- frontend/src/api/.gitkeep
- frontend/src/components/**/.gitkeep
- frontend/src/features/**/.gitkeep
- frontend/src/hooks/.gitkeep
- frontend/src/styles/.gitkeep
- frontend/src/theme/.gitkeep
- frontend/src/utils/.gitkeep

## Data / API / State Requirements

No real API contracts.

## UI Requirements

RTL not required beyond future-ready structure; no actual screens.

## Business Rules

N/A.

## Error Handling

Display safe placeholder if config missing.

## Acceptance Criteria

- Frontend loads.
- Approved folder structure exists.
- No real feature pages.
- No messy inline CSS.

## Required Automated Tests

- Frontend startup/build smoke if approved.

## Contract / Compatibility Tests

N/A.

## Manual Verification

- Open frontend in browser.
- Inspect no out-of-scope features.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- Frontend shell loads.
- No product features implemented.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
