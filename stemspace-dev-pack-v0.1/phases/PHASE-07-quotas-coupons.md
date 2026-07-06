# Phase 07 — Quotas + Coupons

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-07
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Enforce Free/Pro quotas and coupon redemption safely.

## Exact tasks

1. Free: 3 Basic/day.
2. Free blocked from Professional.
3. Pro: 10 Professional/day.
4. Pro Basic displayed as extended/fair use.
5. UsageEvent finalization.
6. DailyUsage update.
7. Coupon redeem.
8. Coupon data model.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- Quota checked before job creation.
- Quota counted only after Ready.
- Both outputs required before usage count.
- Failed does not count.
- Duplicate finalization does not double count.
- Free cannot bypass Professional via API.
- Invalid/expired/used coupon rejected.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

No full billing provider/payment integration or quota scope changes.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Security Review Required
