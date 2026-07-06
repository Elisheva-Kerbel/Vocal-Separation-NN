# Task P0-002 — Docker Compose and Dockerfiles

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

Create the Docker Compose local environment and minimal Dockerfiles.

## Context

The project must use Docker Compose so DB, Redis, MinIO, backend, worker and frontend are wired consistently.

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

- TASK-P0-001 complete or approved file structure exists.

## Entry Criteria

Folder structure exists.

## Required Tools

Filesystem write access; Docker available for validation if approved.

## Forbidden Tools

Production credentials, pushing images, external deployments.

## Write Scope

`docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `backend/.dockerignore`, `frontend/.dockerignore`, `.env.example`.

## Network / External-System Access

No production network. Package installation only if part of approved build validation.

## What to Do

- Define services: postgres, redis, minio, backend, worker, frontend.
- Use service names for internal URLs, not localhost.
- Add named volumes for PostgreSQL and MinIO local data.
- Create backend Dockerfile for FastAPI environment.
- Create frontend Dockerfile for Vite environment.
- Use backend image or target for worker to avoid duplicated dependencies.
- Create `.env.example` with placeholders only.

## What Not to Do

- Do not add business logic.
- Do not run migrations automatically.
- Do not include real secrets.
- Do not add production deployment files.

## Files Likely to Change

- docker-compose.yml
- .env.example
- backend/Dockerfile
- frontend/Dockerfile
- backend/.dockerignore
- frontend/.dockerignore

## Data / API / State Requirements

Service env values are placeholders. Internal DB/Redis/MinIO URLs use Compose service names.

## UI Requirements

No UI beyond container startup.

## Business Rules

Private storage and no real secrets.

## Error Handling

Fail safely on missing env; do not hide config errors.

## Acceptance Criteria

- docker compose config is valid.
- All six services are defined.
- Backend/worker/frontend have build contexts.
- No real secrets.
- Worker reuses backend dependency definition where practical.

## Required Automated Tests

- Compose config validation.
- Dockerfile parse/build smoke if approved.

## Contract / Compatibility Tests

N/A.

## Manual Verification

- Inspect compose services.
- Confirm env placeholders.
- Confirm no production secret values.

## Evidence to Return

- Changed files.
- Checks/tests run.
- Manual verification result.
- Deviations.
- Blockers.
- Confirmation that no out-of-scope work was done.

## Definition of Done

- Compose config valid.
- Dockerfiles exist.
- No over-engineered build system.
- Evidence returned.

## Stop Gate

Stop after this task.
Run only approved checks.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
