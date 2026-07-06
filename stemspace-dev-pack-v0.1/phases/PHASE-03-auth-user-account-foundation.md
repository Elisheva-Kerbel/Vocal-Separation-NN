# Phase 03 — Auth + User Account Foundation

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-03
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Add basic account system and backend-enforced permissions.

## Exact tasks

1. Signup.
2. Login.
3. Current user endpoint.
4. Password hashing.
5. User status active/blocked/deleted.
6. Profile visibility hidden/public.
7. Preferred language.
8. Email opt-in.
9. Backend permission guard.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- User can signup/login.
- /me works.
- Blocked user cannot upload/rate/publish.
- Hidden profile is not publicly returned.
- Permissions enforced in backend.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

No OAuth/social login/password reset/generic admin unless approved.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Security Review Required
