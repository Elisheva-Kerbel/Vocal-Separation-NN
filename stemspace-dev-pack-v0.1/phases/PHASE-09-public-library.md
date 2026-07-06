# Phase 09 — Public Library

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-09
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Add explicit public discovery and sharing after private core flow is stable.

## Exact tasks

1. Publish/unpublish.
2. Publish confirmation.
3. Public library list.
4. Public song page.
5. Rating 1-5.
6. Similar songs by tags.
7. Report content.
8. Hidden profile handling.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- New song private by default.
- Publish requires explicit action.
- Rights checkbox required.
- Public listen follows Legal/Product decision.
- Public download requires login.
- User cannot rate own song.
- One rating per user per song.
- Hidden profile displays private user.
- Public API does not expose hidden owner identity.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

Do not open before private core flow; do not default anything to public.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Do Not Open Yet
