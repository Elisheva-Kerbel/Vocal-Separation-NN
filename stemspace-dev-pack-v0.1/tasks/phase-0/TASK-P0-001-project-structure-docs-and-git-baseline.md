# Task P0-001 — Project Structure, docs/ Task Files and Git Baseline

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

Create the minimal monorepo folder structure, documentation folder and Git baseline files.

## Context

Phase 0 must include a `docs/` folder with clear Markdown task files and files required for safe Git work.

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

- Nadav-approved Phase 0 package.
- No repository business logic exists yet.

## Entry Criteria

Empty or new repository/worktree.

## Required Tools

Filesystem write access inside repo only.

## Forbidden Tools

Package managers, external services, secrets, production credentials.

## Write Scope

`README.md`, `.gitignore`, `.gitattributes`, `.editorconfig`, `docs/`, empty project directories and `.gitkeep` only.

## Network / External-System Access

No external network required.

## What to Do

- Create the approved top-level directory layout.
- Create `docs/README.md`.
- Create `docs/tasks/phase-0/` with Markdown files for the six Phase 0 tasks.
- Create `docs/decisions/DEC-0001-compose-first-local-dev.md`.
- Create `docs/decisions/DEC-0002-minimal-code-no-overengineering.md`.
- Create `.gitignore`, `.gitattributes`, `.editorconfig`.
- Add `.gitkeep` only where empty directories must be retained.

## What Not to Do

- Do not create product code.
- Do not install dependencies.
- Do not add CI workflows.
- Do not add auth/upload/AI/DB domain logic.

## Files Likely to Change

- README.md
- .gitignore
- .gitattributes
- .editorconfig
- docs/README.md
- docs/tasks/phase-0/*.md
- docs/decisions/*.md
- backend/.gitkeep
- frontend/.gitkeep
- infra/.gitkeep
- local-data/.gitkeep

## Data / API / State Requirements

No API or DB state.

## UI Requirements

No UI implementation.

## Business Rules

No product behavior implemented.

## Error Handling

N/A.

## Acceptance Criteria

- Required folder tree exists.
- Required docs task files exist.
- Git baseline files exist.
- No business logic files added.
- No secrets or real credentials.

## Required Automated Tests

- Optional: script-free file existence check.
- No automated product tests required.

## Contract / Compatibility Tests

N/A.

## Manual Verification

- Inspect tree.
- Open docs files.
- Confirm Git baseline files are readable.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- All required files exist.
- No out-of-scope implementation.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
