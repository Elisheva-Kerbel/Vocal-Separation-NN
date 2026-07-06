# Phase 08 — My Library

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-08
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Let user view personal song history and soft delete own songs.

## Exact tasks

1. My Library API.
2. Filters by status/date/tag/privacy.
3. Open result page.
4. Delete song.
5. Soft delete.
6. Cleanup worker for physical deletion.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- User sees only own songs.
- Deleted song disappears.
- Deleted song file access blocked immediately.
- Physical cleanup async.
- Audit/recovery data remains.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

No public discovery, ratings, similar songs or admin moderation.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

UX Spec Required
