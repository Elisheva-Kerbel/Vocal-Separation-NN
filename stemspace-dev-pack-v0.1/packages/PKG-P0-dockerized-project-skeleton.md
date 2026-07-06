# Package PKG-P0 — Dockerized Project Skeleton

Artifact Type: Outcome Package
Artifact ID: PKG-P0
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact package/version before transfer
Execution allowed: No

## Verifiable Outcome

`docker compose up` can start PostgreSQL, Redis, MinIO, backend, worker and frontend from a minimal monorepo skeleton with docs and Git baseline files.

## Business / Technical Value

Creates a repeatable local development foundation without product business logic.

## Source References

- User-provided StemSpace technical handoff.
- Pack baseline files `01-project-context.md`, `02-product-scope-and-do-not-build.md`, `04-minimal-code-policy.md`.

## Ownership and Authorities

- Prepared by: Eitan
- Product authority: Mika
- Architecture authority: Ariel
- Technical decision authority: Noa
- UX authority: Tamar
- SAP authority: Not applicable for this package unless later introduced
- QA reviewer: Nadav
- Authorized transfer operator: Not assigned in this artifact

## Dependencies

### Direct

- User-provided Compose-first requirement.
- Locked stack in handoff.

### Transitive

- Nadav review before transfer.
- No secrets policy.
- Minimal-code policy.

## Required Decisions and Contract Freezes

- Compose-first local development is incorporated as a user requirement.
- No CI/CD workflow in Phase 0 unless Noa approves it.

## Required Access, Environment and Test Data

- Local Docker environment.
- No production credentials.
- No real secrets.

## Definition of Ready

- [ ] Source baseline is recorded.
- [ ] Required decisions are approved or explicitly isolated.
- [ ] Dependencies are satisfied or scoped out.
- [ ] Test data exists when required.
- [ ] Evidence contract is defined.
- [ ] Nadav can review the package.

## Startability

Startable as draft after Nadav review.

## Closability

Closable only after startup evidence exists and Nadav reviews the evidence.

## Critical-Path and Risk Notes

Critical path foundation. If Docker Compose is wrong, all downstream phases inherit environment instability.

## Tasks

- `tasks/phase-0/TASK-P0-001-project-structure-docs-and-git-baseline.md`
- `tasks/phase-0/TASK-P0-002-docker-compose-and-dockerfiles.md`
- `tasks/phase-0/TASK-P0-003-backend-health-and-config.md`
- `tasks/phase-0/TASK-P0-004-worker-startup-stub.md`
- `tasks/phase-0/TASK-P0-005-frontend-empty-shell.md`
- `tasks/phase-0/TASK-P0-006-readme-and-coding-rules.md`

## Safe Parallel Work

- Backend health and frontend shell can be parallel after folder structure exists.
- Worker stub can be parallel with frontend shell if Compose service names are fixed.

## Must Be Sequential

- Folder/docs/git baseline before Compose references files.
- Compose before container startup verification.

## Write / Tool Boundaries

- Write only skeleton, config, docs and startup stubs.
- No business logic.
- No external network except package installation during implementation if approved by Nadav.

## Deliverables

- Repo folder structure.
- Docker Compose.
- Dockerfiles.
- docs/ Markdown task files.
- Git baseline files.
- README and coding rules.
- Health and startup stubs.

## Automated Tests

- Backend health test.
- Compose config validation.
- Frontend startup/build smoke check.
- Worker import/start smoke check.

## Provider / Consumer Contract Tests

No API contract beyond `/health` in Phase 0.

## Cross-Package Integration Verification

Verify backend, worker, DB, Redis and MinIO resolve via Docker Compose service names.

## Manual Verification

- Start all services in local Compose.
- Open frontend.
- Call backend health.
- Confirm worker starts.

## Evidence Contract

Return:
- changed files;
- tests/checks run;
- manual verification;
- screenshots or command outputs where relevant;
- deviations;
- blockers;
- confirmation that no out-of-scope work was done.

## Operational Readiness

- Local volumes for PostgreSQL and MinIO.
- Clear README local startup notes.
- No production operational claims.

## Rollback / Recovery

Remove generated skeleton files or reset branch. No data migration exists in Phase 0.

## Exit Criteria

- All acceptance criteria pass.
- Evidence report is returned.
- No business logic exists.

## Approval Gate

Nadav must review and explicitly PASS this exact package version before authorized transfer.

## Unlocks

P1 AI Benchmark Harness and P2 Backend Domain + DB Skeleton.

## Open Blockers

Nadav PASS missing for transfer.

## Do Not Build

- Auth.
- Upload.
- AI inference.
- DB domain models.
- Public Library.
- Admin.
- Billing.
