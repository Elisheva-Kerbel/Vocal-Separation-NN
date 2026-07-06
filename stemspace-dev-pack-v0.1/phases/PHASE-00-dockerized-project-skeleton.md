# Phase 00 — Dockerized Project Skeleton

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-00
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Create a clean, minimal monorepo foundation that starts via Docker Compose without business logic.

## Exact tasks

1. Create approved folder structure.
2. Add docs/ directory with clear Markdown task files for Phase 0.
3. Add Git baseline files: .gitignore, .gitattributes, .editorconfig.
4. Add docker-compose.yml for PostgreSQL, Redis, MinIO, backend, worker and frontend.
5. Add backend/Dockerfile and frontend/Dockerfile.
6. Add .env.example with placeholders only.
7. Add backend /health.
8. Add frontend empty Vite app.
9. Add worker startup stub.
10. Add README and coding rules.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- docker compose config passes.
- docker compose up starts all local services.
- Backend /health works.
- Frontend loads.
- Worker starts.
- DB/Redis/MinIO reachable by service name.
- No business logic.
- No real secrets.
- No inline CSS mess.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

Do not implement auth, upload, AI inference, DB domain models, public library, admin or billing.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Ready for Nadav Readiness Review
