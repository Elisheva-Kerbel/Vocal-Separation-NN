# Phase 05 — Queue + Worker Processing

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-05
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Process uploaded songs asynchronously using Redis + Celery.

## Exact tasks

1. Configure Celery.
2. Create SeparationJob.
3. Create worker task.
4. Worker downloads original.
5. Worker runs inference.
6. Worker uploads Vocals and Background.
7. Update job/song states.
8. Retry behavior.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- Uploaded song creates queued job.
- States Uploaded/In Queue/Processing/Ready/Failed.
- Ready only when both outputs exist.
- Failed does not count quota.
- Retry creates new attempt/job.
- Worker failure does not corrupt DB.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

No professional separate queue; no billing; no public library; no processing inside API request.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Ready after Phase 1 + Phase 4
