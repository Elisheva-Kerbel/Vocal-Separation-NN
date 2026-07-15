# P2-002 — Domain Models

Status: **BLOCKED — guardrails only. Not authorized. Open product decisions must close first.**
Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2
Depends on: P2-001 complete (authorized + accepted) · `docs/decisions/DEC-0005` · **open decisions below**
Baseline: `stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-002-domain-models.md`

> **Guardrails only. Do not implement.** This document exists so that the security and design
> boundaries are unambiguous **before** anyone writes an entity. It authorizes no models, no
> migrations and no code. P2-002 is the highest-stakes task in Phase 2: the data model it creates
> gates P3 and P4, and PKG-P2 warns that "contract changes after this point can stale later
> evidence."

## Blocking open decisions

P2-002 **must not start** until these are decided by the human authorities. They are **not** resolved
by DEC-0005, which covers the DB *foundation* only.

1. **Song and SeparationJob state values.** PKG-P2 says state names "should be reviewed before
   closure"; they are defined **nowhere** in the pack. Only `PHASE-03` names User
   `active/blocked/deleted`.
2. **Field-level definitions for the 14 entities.** The pack names `User`, `Song`, `AudioFile`,
   `SeparationJob`, `Tag`, `SongTag`, `Rating`, `Coupon`, `CouponRedemption`, `DailyUsage`,
   `UsageEvent`, `SignedUrlGrant`, `ContentReport`, `AdminAuditEvent` — and specifies **zero fields**.
   Created/updated timestamps are never mentioned anywhere in the pack.
3. **UsageEvent uniqueness key.** "Unique success finalization by song" is an intent, not a key —
   `(song_id)` vs `(user_id, song_id)` vs `(user_id, song_id, date)` is undecided, and the success
   state it keys on does not exist until (1) closes.
4. **`storage_key` format and owning entity.** That it stays internal is clear; its shape is not.

**Rule:** if these are still open when P2-002 is prompted, **stop and report a blocker**. Do not
invent entity fields, state values or uniqueness keys. The source task's instruction to "add fields
needed for MVP and future phases" is **not** authorization to design the data contract —
`docs/coding-rules.md` §9: "No product or architecture decisions by the code agent."

## Security guardrails (binding when P2-002 is later authorized)

- **no audio bytes in DB.** Audio lives in private object storage; the DB holds metadata only.
- **No `LargeBinary` / `BYTEA` audio columns** — on any entity, for any reason.
- **no checkpoint/model/local filesystem paths in DB.** No column, default, comment, seed value or
  migration may store a checkpoint path, model path, weights filename or operator-machine filesystem
  path. `SeparationJob` may carry at most a logical **`modelTier`**, never a path (`AGENT.md`,
  `DEC-0004` §5).
- **No `LOCAL_MODEL_ROOT` value in DB.** Environment-only and out-of-band per `DEC-0004`.
- **no signed URL string in DB.** Signed URLs are short-lived credentials and are never persisted
  (`DEC-0003`, `06-security-permissions-and-secrets.md`).
- **`SignedUrlGrant` stores grant/audit metadata only** — subject, resource, grant time, expiry —
  and **never the signed URL string**. The grant is an audit fact; the URL is a secret.
- **No public storage URLs** — no public bucket, no public object URL, no permanent file URL.
- **`storage_key` is internal only.** It may exist on internal DB/domain models where a later phase
  genuinely needs it, and **`storage_key` must not be exposed** in client/API schemas (see P2-003).
- **Do not expose DB models as API schemas.** DB model ≠ API schema (PKG-P2 contract).
- **`DATABASE_URL` must not be logged or echoed** — including in model/migration error paths.
- Minimal model set: **no unapproved entities**, no over-normalization, no speculative fields
  (`DEC-0002`).

## Required tests when implemented

Beyond the source task's "model creation" and "migration" tests, these are **required** — the
readiness gate found the audio-byte rule was an acceptance criterion with **manual inspection only**
behind it, which leaves a High-severity risk (`R-004` neighbourhood) unguarded:

1. **Automated no-audio-bytes-in-DB test.** Assert that **no** `LargeBinary` / `BYTEA` column exists
   anywhere in `Base.metadata`. This converts a manual check into a permanent regression guard and is
   cheap to write.
2. **Automated no-path-columns test.** Assert no entity carries a checkpoint/model/local filesystem
   path field.
3. **Model creation test** and **migration test** (per the source task).
4. **Deterministic migration check** — constraint/index names follow the DEC-0005 naming convention;
   no backend-generated names.
5. **State values match the approved decision** once it exists — not free-form strings.

## Out of scope

API routes; services; upload; queue; Redis; storage client; signed URL generation; AI integration;
frontend; worker processing; production DB; production migrations; auth/billing/admin/public
library/resumable upload/extra stems.

## Stop gate

Do not start. P2-002 begins only after P2-001 is accepted **and** the blocking open decisions above
are recorded by their authorities **and** an explicit prompt authorizes it. If prompted while
decisions are open: **report a blocker, implement nothing.**
