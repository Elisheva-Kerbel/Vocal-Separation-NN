# Phase 02 — Backend Domain + DB Skeleton

Artifact Type: Delivery Phase
Artifact ID: STEMSPACE-PHASE-02
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT / DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + pack baseline
Prepared by: Eitan
Required approval: Nadav readiness review before transfer
Execution allowed: No

## Purpose

Create DB foundation, domain models, migrations and schemas without storing audio bytes in DB.

## Exact tasks

1. Create SQLAlchemy base/session.
2. Create Alembic setup.
3. Create User, Song, AudioFile, SeparationJob, Tag, SongTag, Rating, Coupon, CouponRedemption, DailyUsage, UsageEvent, SignedUrlGrant, ContentReport, AdminAuditEvent.
4. Create Pydantic schemas.
5. Create migration.
6. Create seed tags script.
7. Add tests.

## Files to create/change

See the matching package and task files.

## Inputs required

- Approved source baseline for this phase.
- Required decisions listed in `10-open-decisions-and-blockers.md`.
- No secrets in chat, task files or repo.

## Output expected

A verifiable outcome for this phase only.

## Acceptance criteria

- Alembic upgrade head succeeds.
- No audio bytes stored in DB.
- storage_key internal only.
- API schemas do not expose storage keys.
- UsageEvent supports unique success finalization by song.

## Tests required

- Automated tests listed in the matching task files.
- Manual verification listed in the matching task files.
- Evidence report using `templates/evidence-report-template.md`.

## What not to change

Do not implement upload/auth/worker/admin/public/coupons UI.

## Dependencies / blockers

See `08-dependency-map-and-critical-path.md`.

## Phase readiness label

Nadav Readiness Review
