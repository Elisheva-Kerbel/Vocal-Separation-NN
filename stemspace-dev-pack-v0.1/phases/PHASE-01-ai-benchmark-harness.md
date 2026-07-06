# Phase 01 — AI Benchmark Harness

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-01
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Run real audio separation outside the API before connecting upload, queue or DB.

## Exact tasks

1. Create backend/ai module boundaries.
2. Create checkpoint registry.
3. Create benchmark CLI.
4. Produce vocals/background/metrics JSON.
5. Support modelTier.
6. Keep checkpoint selection server-side.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- CLI processes one real audio file.
- Both output files generated.
- Metrics JSON includes runtime/decode/inference/encode/output sizes/success/failure.
- No checkpoint path accepted from client-style input.
- No API/queue integration.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

Do not connect to upload API; do not add Celery processing; do not support extra stems.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Ready for Spike
