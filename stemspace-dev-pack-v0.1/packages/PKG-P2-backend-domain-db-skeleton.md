# Package PKG-P2 — Backend Domain + DB Skeleton

Artifact Type: Outcome Package
Artifact ID: PKG-P2
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact package/version before transfer
Execution allowed: No

## Verifiable Outcome

Database foundation, domain models, migrations and schemas exist without storing audio bytes in DB or exposing storage keys.

## Business / Technical Value

Establishes the safe data baseline needed for auth, upload, processing, quotas, public/private visibility and audit.

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

- P0 Dockerized Project Skeleton.
- Approved model list from handoff.

### Transitive

- Future Upload/Worker/Quota contracts.
- Security rule that storage keys are internal.

## Required Decisions and Contract Freezes

- State names for Song and SeparationJob should be reviewed before closure.
- Idempotency strategy for UsageEvent should be compatible with Phase 7.

## Required Access, Environment and Test Data

- Local PostgreSQL through Docker Compose.
- No production DB.
- No secrets.

## Definition of Ready

- [ ] Source baseline is recorded.
- [ ] Required decisions are approved or explicitly isolated.
- [ ] Dependencies are satisfied or scoped out.
- [ ] Test data exists when required.
- [ ] Evidence contract is defined.
- [ ] Nadav can review the package.

## Startability

Startable after P0.

## Closability

Closable after migration evidence and schema leak tests pass.

## Critical-Path and Risk Notes

Shared data model controls many downstream phases. Contract changes after this point can stale later evidence.

## Tasks

- `tasks/phase-2/TASK-P2-001-db-base-and-alembic.md`
- `tasks/phase-2/TASK-P2-002-domain-models.md`
- `tasks/phase-2/TASK-P2-003-pydantic-schemas-no-storage-key-leak.md`
- `tasks/phase-2/TASK-P2-004-seed-tags-and-db-tests.md`

## Safe Parallel Work

- Schema leak tests can be drafted after model fields are known.
- Seed tags can be drafted after Tag model exists.

## Must Be Sequential

- DB base before models.
- Models before migration.
- Migration before migration tests.

## Write / Tool Boundaries

- Write only backend DB/models/schemas/migrations/tests/scripts for domain skeleton.
- No API routes except existing health.

## Deliverables

- SQLAlchemy base/session.
- Alembic migration.
- Domain models.
- Pydantic schemas.
- Seed tags script.
- Tests.

## Automated Tests

- Migration test.
- Model creation test.
- Schema serialization test.
- Storage key leak prevention test.

## Provider / Consumer Contract Tests

DB model is not API schema. API schemas must not expose `storage_key` or internal file refs.

## Cross-Package Integration Verification

P3/P4/P5 depend on this data model; downstream closure requires compatibility tests.

## Manual Verification

- Run migration against local Postgres.
- Inspect schema.
- Confirm no storage keys in external schema output.

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

- Migrations must be deterministic.
- No auto-running destructive migrations on container start unless later approved.

## Rollback / Recovery

Rollback migration in local dev only; no production migration exists.

## Exit Criteria

- Alembic upgrade head succeeds.
- Tests pass.
- Storage key leak test proves external schemas are safe.

## Approval Gate

Nadav must review and explicitly PASS this exact package version before authorized transfer.

## Unlocks

P3 Auth and P4 Upload + Private Storage.

## Open Blockers

Nadav PASS missing; direct PRD/architecture artifact confirmation still recommended.

## Do Not Build

- Upload endpoint.
- Auth routes.
- Worker processing.
- Admin.
- Public Library.
- Coupon UI.
