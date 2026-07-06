# Phase 06 — Result Page + Secure File Access

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-06
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Let user view status and securely listen/download outputs through signed URLs.

## Exact tasks

1. GET /songs/{songId}.
2. GET /songs/{songId}/status.
3. listen-url endpoint.
4. download-url endpoint.
5. Backend permission checks.
6. SignedUrlGrant audit.
7. Frontend Result Page.
8. Audio players.
9. Download buttons.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- Owner can listen/download.
- Unauthorized blocked.
- Public download requires login.
- Download TTL <=5 min.
- Listen TTL <=10 min.
- Signed URL not stored in DB.
- Grant event stored.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

No public default; no storage key exposure; no permanent URL.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Security Review Required + UX Spec Required
