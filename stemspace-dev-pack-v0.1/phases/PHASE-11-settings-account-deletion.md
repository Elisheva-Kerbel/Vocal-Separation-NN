# Phase 11 — Settings + Account Deletion

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-11
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Support user privacy settings and safe account deletion.

## Exact tasks

1. Settings page.
2. Language preference.
3. Email opt-in.
4. Profile visibility.
5. Delete account form.
6. Deletion worker.
7. Remove/delete public songs by default.
8. Delete private files.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- Profile hidden by default.
- Hidden profile endpoint returns 404/403.
- Deletion requires explicit confirmation.
- Private files deleted.
- Public songs removed/deleted by default.
- Signed URLs not renewed and expire naturally.
- Minimal audit/tombstone kept.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

No hard delete without approved retention policy; no irreversible action without recovery plan.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Security Review Required + UX Spec Required
