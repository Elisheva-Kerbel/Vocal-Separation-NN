# Phase 10 — Admin RBAC + Audit

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-10
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Add scoped admin operations with backend RBAC and audit.

## Exact tasks

1. Admin API namespace.
2. Roles: Content Moderator, User Admin, Coupon Admin, Super Admin.
3. Content moderation.
4. User blocking.
5. Coupon management.
6. Report handling.
7. Admin audit.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- No generic daily-use admin.
- Each endpoint checks backend role.
- Content Moderator cannot access private audio.
- User Admin cannot manage coupons unless allowed.
- Coupon Admin cannot remove content.
- All changes audited.
- Removed song disappears from public surfaces.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

No generic admin role; no private audio access for moderators; no unaudited destructive action.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Do Not Open Yet / Security Review Required
