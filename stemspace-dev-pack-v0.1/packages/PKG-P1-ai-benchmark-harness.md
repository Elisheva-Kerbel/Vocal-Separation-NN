# Package PKG-P1 — AI Benchmark Harness

Artifact Type: Outcome Package
Artifact ID: PKG-P1
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact package/version before transfer
Execution allowed: No

## Verifiable Outcome

A CLI can process one real audio file outside the API and produce Vocals, Background and metrics JSON.

## Business / Technical Value

Reduces AI/model uncertainty before connecting upload, queue or DB.

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
- Initial model/checkpoint availability.

### Transitive

- Server-side checkpoint decision.
- Safe local test audio fixture.

## Required Decisions and Contract Freezes

- Initial model/checkpoint source must be approved or explicitly treated as spike-only.

## Required Access, Environment and Test Data

- Local/backend Python environment.
- Local test audio file.
- No production storage.
- No client-supplied checkpoint path.

## Definition of Ready

- [ ] Source baseline is recorded.
- [ ] Required decisions are approved or explicitly isolated.
- [ ] Dependencies are satisfied or scoped out.
- [ ] Test data exists when required.
- [ ] Evidence contract is defined.
- [ ] Nadav can review the package.

## Startability

Ready for Spike after P0.

## Closability

Closable only after a real audio benchmark produces both outputs and metrics.

## Critical-Path and Risk Notes

High-risk proof-of-feasibility. Do not hide model uncertainty inside API work.

## Tasks

- `tasks/phase-1/TASK-P1-001-ai-module-boundaries.md`
- `tasks/phase-1/TASK-P1-002-checkpoint-registry-and-model-tier.md`
- `tasks/phase-1/TASK-P1-003-benchmark-cli-and-metrics.md`
- `tasks/phase-1/TASK-P1-004-real-audio-validation.md`

## Safe Parallel Work

- Metrics schema and checkpoint registry can be drafted before real audio validation.

## Must Be Sequential

- Real audio validation after CLI and model path are defined.

## Write / Tool Boundaries

- Write only under `backend/ai`, `backend/scripts`, `backend/tests/ai`, and docs/spike.
- No API, DB or queue changes.

## Deliverables

- AI module boundaries.
- Checkpoint registry.
- Benchmark CLI.
- Metrics schema.
- Spike documentation.

## Automated Tests

- Checkpoint tier mapping test.
- Metrics schema test.
- Invalid checkpoint path rejection test.
- Manual real audio benchmark.

## Provider / Consumer Contract Tests

`modelTier` accepted as logical input; checkpoint selection remains internal.

## Cross-Package Integration Verification

None with Upload API or Celery in this phase.

## Manual Verification

- Run CLI against a local audio fixture after approval.
- Inspect vocals/background outputs.
- Inspect metrics JSON.

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

- Benchmark output directory should be ignored by Git.
- Large model/checkpoint files must not be committed.

## Rollback / Recovery

Remove benchmark artifacts and generated output files. No DB migration.

## Exit Criteria

- CLI works with real audio.
- Outputs and metrics exist.
- No API/queue integration added.

## Approval Gate

Nadav must review and explicitly PASS this exact package version before authorized transfer.

## Unlocks

P5 Queue + Worker Processing.

## Open Blockers

Approved/checkpoint source and test audio fixture may block closure.

## Do Not Build

- Upload API integration.
- Celery worker integration.
- DB writes.
- Extra stems.
