# Phase 04 — Upload + Private Storage

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-04
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Upload real files into private storage with validation and no public URLs.

## Exact tasks

1. Storage adapter.
2. Storage key generator.
3. Upload API.
4. Validate mp3/m4a/wav.
5. Validate max 100MB.
6. Validate max 5.5 minutes.
7. Require auth.
8. Check quota availability.
9. Save original privately.
10. Create Song and AudioFile.
11. Cleanup failed upload.
12. Frontend upload skeleton with progress.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- Invalid format blocked.
- Over-size blocked.
- Over-duration blocked.
- No job on validation failure.
- No public URL returned.
- No storage key returned.
- Progress works.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

No resumable upload; no public bucket; no permanent URL; no inference in HTTP request.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Security Review Required
