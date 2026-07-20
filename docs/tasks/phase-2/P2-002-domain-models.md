# P2-002 — Domain Models

Status: **Decisions closed by DEC-0006 — pending Nadav implementation authorization. Do not implement yet.**
Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2
Depends on: P2-001 complete (accepted) · `docs/decisions/DEC-0005` · **`docs/decisions/DEC-0006` (domain data contract)**
Baseline: `stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-002-domain-models.md`

> **Contract closed, not yet authorized.** The four blocking open decisions below are now **resolved
> by `docs/decisions/DEC-0006`**. This document plus DEC-0006 are the active implementation contract.
> Implementation still requires an **explicit Nadav authorization** — do not write models, migrations
> or code until it is issued. P2-002 is the highest-stakes task in Phase 2: the data model it creates
> gates P3 and P4, and PKG-P2 warns that "contract changes after this point can stale later evidence."

## Closed decisions (see DEC-0006)

The four decisions that previously blocked P2-002 are now decided in `docs/decisions/DEC-0006`; the
code agent must **not** re-decide them:

1. **Song and SeparationJob state values** — fixed in DEC-0006 §3-enums
   (`Song`: `uploaded/processing/ready/failed`; `SeparationJob`:
   `queued/running/succeeded/failed/canceled`; `User`: `active/blocked/deleted`;
   `AudioFile.purpose`: `original/vocals/background`).
2. **Field-level definitions + timestamps** — fixed per-entity in DEC-0006 §4, with the global
   `id`/`created_at`/`updated_at`/UTC/nullable conventions in §3.
3. **UsageEvent uniqueness key** — fixed as **`UNIQUE(song_id, event_type)`** with
   `separation_succeeded` finalising once per song only after `succeeded`+`ready` (DEC-0006 §8;
   `R-005`/`R-006`).
4. **`storage_key` format and owning entity** — fixed on `AudioFile` as an opaque internal key,
   internal-only, never in API schemas (DEC-0006 §5).

**Scope (DEC-0006 §2, §12):** P2-002 implements **8 tables** — `User`, `Song`, `AudioFile`,
`SeparationJob`, `Tag`, `SongTag`, `UsageEvent`, `DailyUsage`. The other 6 entities (`Rating`,
`Coupon`, `CouponRedemption`, `SignedUrlGrant`, `ContentReport`, `AdminAuditEvent`) have their
contract defined in DEC-0006 but their **table creation is deferred** to their approved phases — do
not create them now.

**Rule:** implement exactly the DEC-0006 contract. Do not invent fields, states, keys, indexes or
entities, and do not pull deferred tables forward — `docs/coding-rules.md` §9: "No product or
architecture decisions by the code agent."

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

The full, closed test contract is **DEC-0006 §13**; it supersedes the source task's undefined
"model creation / migration" tests. All of the following must pass:

1. **Expected tables** — `Base.metadata` contains exactly the 8 implemented tables (no deferred or
   extra table).
2. **Expected columns** — each entity has exactly the DEC-0006 §4 fields (name + nullability).
3. **Enum values** — each enum column allows exactly the DEC-0006 §3-enums set (asserted against the
   `CHECK`), never free-form strings.
4. **Relationships** — the DEC-0006 §9 foreign keys exist and point at the right tables.
5. **Uniqueness constraints** — `users.email`; `audio_files (song_id, purpose)` and `storage_key`;
   `tags.slug`; `song_tags` composite PK; **`usage_events (song_id, event_type)`**;
   **`daily_usage (user_id, usage_date)`**.
6. **Indexes** — the DEC-0006 §10 indexes exist with DEC-0005-convention names (no
   backend-generated names).
7. **No audio-bytes columns** — assert **no `LargeBinary` / `BYTEA`** column anywhere in
   `Base.metadata` (converts the previously manual-only check into a permanent guard; `R-004`).
8. **No checkpoint/model/local-path columns** — no `checkpoint_path`, `model_path`,
   `local_model_root`, `local_path` or filesystem-path field on any entity.
9. **No signed-URL-string columns** — no `signed_url` / URL-token column on any entity.
10. **No public-URL columns** — no public/permanent object-URL column.
11. **`storage_key` internal only** — present on `AudioFile`; the P2-003 schema test proves it is not
    serialised into any API/client schema.
12. **`modelTier` logical only** — `SeparationJob.model_tier` is the string enum `basic`, never a path.
13. **UsageEvent idempotency uniqueness** — the `(song_id, event_type)` unique constraint exists.
14. **DailyUsage uniqueness** — the `(user_id, usage_date)` unique constraint exists.
15. **Alembic compatibility** — the initial migration builds the 8 tables; a second autogenerate is
    stable (deterministic DEC-0005 names, no drift).
16. **Existing P2-001 tests still pass** — DB base/session/config/Alembic-scaffold suite unaffected.
17. **Phase 0/1 regressions still pass** — `/health`, config, worker startup and the AI-boundary
    lazy-import test are unaffected.

## Out of scope

API routes; services; upload; queue; Redis; storage client; signed URL generation; AI integration;
frontend; worker processing; production DB; production migrations; auth/billing/admin/public
library/resumable upload/extra stems.

## Stop gate

P2-001 is accepted and the blocking decisions are now recorded in `docs/decisions/DEC-0006`. P2-002
begins only after an **explicit Nadav implementation authorization** for P2-002. Until that prompt is
issued, **implement nothing** — no models, no migration, no code. When authorized, implement exactly
the DEC-0006 contract (the 8 implemented tables), run the §"Required tests when implemented" contract,
and stop; do not continue to P2-003.
