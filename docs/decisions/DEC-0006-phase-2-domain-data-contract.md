# DEC-0006 — Phase 2 domain data contract

Status: **Approved for P2-002 planning / pending Nadav implementation authorization.**
Not an implementation authorization. Not production-approved. No public users. No commercial approval.

Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2 · Recorded by: DEC-0006 domain-contract work
Relates to: `DEC-0002` (minimal code), `DEC-0003` (private storage only), `DEC-0004` (local model prototype),
`DEC-0005` (DB base / session / migration determinism), `docs/coding-rules.md`, `docs/tasks/phase-2/P2-002-domain-models.md`
Baseline (read-only historical): `stemspace-dev-pack-v0.1/phases/PHASE-02-backend-domain-db-skeleton.md`,
`stemspace-dev-pack-v0.1/packages/PKG-P2-backend-domain-db-skeleton.md`,
`stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-002-domain-models.md`,
`stemspace-dev-pack-v0.1/09-risk-register.md`, `stemspace-dev-pack-v0.1/06-security-permissions-and-secrets.md`

> This record closes the four open decisions that made the P2-002 readiness gate report **BLOCKED**
> (entity fields, state values, uniqueness/idempotency keys, and `storage_key` shape). It defines the
> **positive** data contract so P2-002 can later be implemented **mechanically**, without the code
> agent inventing product or architecture decisions (`docs/coding-rules.md` §9). It authorizes **no**
> code, **no** migration, **no** database connection. P2-002 begins only after Nadav reviews this
> record and issues an explicit implementation authorization (see §14).

## 1. Decision

Fix the Phase 2 domain data contract: the **field, state, relationship, uniqueness/idempotency,
index, and storage-reference** definitions for the 14 named entities, built on the DB foundation from
DEC-0005 (PostgreSQL + sync SQLAlchemy 2.x `DeclarativeBase` + Alembic, deterministic naming
convention). The model is the **smallest set sufficient** for the MVP core flow —
**upload → async separation → private result metadata → usage tracking** — plus tag organisation. It
adds **no** product features, **no** entities beyond the 14, and stores **no** audio bytes, secrets,
signed URLs, or model/local paths.

Six entities whose governing behaviour is **not authorized in Phase 2** (ratings, coupons/billing,
signed-URL issuance, public-library reporting, admin/RBAC audit) have their contract **pre-defined
here** but their table creation **deferred** to their approved phase (§4, §11, §12). This keeps
P2-002 minimal (`DEC-0002`, `R-009`) while ensuring the contract exists before those phases begin.

## 2. Scope split — implemented in P2-002 vs deferred

**Implemented in P2-002 (8 tables) — the core flow + tag organisation:**
`User`, `Song`, `AudioFile`, `SeparationJob`, `Tag`, `SongTag`, `UsageEvent`, `DailyUsage`.

**Deferred (6 tables) — contract defined here, creation deferred to the named phase:**
`Rating`, `Coupon`, `CouponRedemption`, `SignedUrlGrant`, `ContentReport`, `AdminAuditEvent`.

No entity is removed; the deferred six are explicitly marked and justified in §4/§11. Deferral moves
only **when the table is created**, never whether the contract is decided.

## 3. Global conventions

Binding on every Phase 2 table.

| Convention | Decision |
|---|---|
| Table names | **plural `snake_case`** (`users`, `songs`, `audio_files`, `separation_jobs`, `tags`, `song_tags`, `usage_events`, …). `daily_usage` is an explicit aggregate-table exception kept singular. Plural avoids the PostgreSQL `user` reserved-word clash. |
| Primary key | **`id`, type UUID** (SQLAlchemy 2.x `Uuid`, native PostgreSQL `uuid`), **application-assigned `uuid4`** (not a DB default) so an id is known before insert and can compose an `AudioFile.storage_key`. One id style for every table. |
| Foreign keys | `<referent_singular>_id` UUID referencing `<referent_table>.id`; constraint names follow the DEC-0005 `fk` pattern. No `ON DELETE` cascade wired in Phase 2 (deletion is not implemented; see soft/hard-delete row). |
| `created_at` | **required (`NOT NULL`) on every table**, timezone-aware, set on insert. |
| `updated_at` | **required on mutable tables** (`users`, `songs`, `audio_files`, `separation_jobs`, `tags`, `daily_usage`; deferred `coupons`, `content_reports`, `ratings`), set on insert and refreshed on update. **Append-only tables carry `created_at` only** (`song_tags`, `usage_events`; deferred `coupon_redemptions`, `signed_url_grants`, `admin_audit_events`). |
| Timezone | **All timestamps timezone-aware, stored in UTC** (`TIMESTAMP WITH TIME ZONE`). No naive datetimes. |
| Nullability | **`nullable=False` by default.** A column is nullable only where this record states it explicitly. |
| Soft vs hard delete | **No soft-delete mechanism in Phase 2** — no `deleted_at`, no `is_deleted`. `User.status` carries block/delete *intent*; actual account-deletion / retention / tombstone behaviour is deferred (OD-007, Phase 11). No cascade deletion is defined beyond safe association-row cleanup (`song_tags`), which is wired only when deletion is later implemented. |
| Enum storage | **Stored as `str` columns with explicit allowed values**, enforced by a **named `CHECK` constraint** (so the DEC-0005 `ck` pattern yields a deterministic name, e.g. `ck_songs_status_allowed`). **No native PostgreSQL `ENUM` type** (keeps migrations simple and alter-safe). Allowed values are the exact sets in §3-enums below. |
| Indexes / constraints | All index, unique, check, fk and pk names come from the **DEC-0005 naming convention** — no backend-generated names. Every `CHECK`/`UniqueConstraint`/`Index` is given an explicit name-yielding definition. |

### 3-enums. Status / enum value decisions (exact, closed)

| Field | Allowed values (exact) | Notes |
|---|---|---|
| `User.status` | `active`, `blocked`, `deleted` | Only status set named in the pack (PHASE-03). `deleted` is an intent marker; real deletion behaviour is Phase 11. Default `active`. |
| `Song.status` | `uploaded`, `processing`, `ready`, `failed` | Minimal upload→result lifecycle. `uploaded` = original stored, not yet processed; `processing` = a job is running; `ready` = outputs available; `failed` = processing failed. Default `uploaded`. |
| `SeparationJob.status` | `queued`, `running`, `succeeded`, `failed`, `canceled` | Explicit minimal async lifecycle. Default `queued`. |
| `AudioFile.purpose` | `original`, `vocals`, `background` | Exactly these. No extra value in Phase 2. |
| **Stem type values** | `vocals`, `background` | The two output stems only (`AudioFile.purpose` minus `original`). **No extra stems** (`02-product-scope`, AGENT.md). |
| `SeparationJob.model_tier` | `basic` | **Logical enum only, never a path.** `basic` is the only tier the local prototype supports (`DEC-0004`); Professional is **not implemented**. Nullable. |
| `UsageEvent.event_type` | `separation_succeeded` | The single **billable / final** usage event in Phase 2. Extensible in its approved billing/quota phase (P7); no other values now. |
| `SignedUrlGrant.purpose` *(deferred)* | `download`, `listen` | Matches the signed-URL TTL classes (`06-security`: download ≤ 5 min, listen ≤ 10 min). |
| `ContentReport.status` *(deferred)* | `open`, `reviewed`, `dismissed` | Minimal moderation lifecycle. Default `open`. |
| `Coupon.status` *(deferred)* | `active`, `disabled` | Minimal; discount/value semantics are a billing-phase decision. |
| `AdminAuditEvent.event_type` *(deferred)* | `url_grant`, `publish`, `admin_removal`, `account_deletion` | Exactly the audit events `06-security` requires. |

## 4. Per-entity field contract

Notation: `PK` primary key · `FK→` foreign key · `U` unique · `IX` index · `enum` string+CHECK ·
`null` nullable · every table has `created_at`; mutable tables also have `updated_at` (per §3).

### 4.1 User — table `users` — **IMPLEMENTED**
- **Required:** `id` PK UUID · `email` str **U** (`uq_users_email`; stored lowercased) · `status` enum
  (`active|blocked|deleted`, default `active`) · `created_at` · `updated_at`.
- **Optional:** *(none in P2)*.
- **FK / relationships:** owns `songs` (1:N), `daily_usage` (1:N); referenced by deferred
  `ratings`, `coupon_redemptions`, `signed_url_grants`, `content_reports`, `admin_audit_events`,
  `usage_events`.
- **Unique / index:** `uq_users_email`.
- **Security / privacy:** `email` is PII, not a secret credential. **No password / auth-credential
  columns in P2** — authentication (password hash, sessions, tokens) is Phase 3 and is not designed
  here. No secrets stored.

### 4.2 Song — table `songs` — **IMPLEMENTED**
- **Required:** `id` PK UUID · `user_id` **FK→**`users.id` (owner) · `status` enum
  (`uploaded|processing|ready|failed`, default `uploaded`) · `created_at` · `updated_at`.
- **Optional:** `title` str **null** — display name, sanitised, never used as a storage path.
- **FK / relationships:** owner `User`; has `audio_files` (1:N), `separation_jobs` (1:N),
  `song_tags` (M:N `tags`); referenced by deferred `ratings`, `content_reports`.
- **Unique / index:** `IX` on `(user_id, created_at)` (owner's recent songs); `IX` on `status`.
- **Security / privacy:** **No storage reference on `Song`** (those live on `AudioFile`). **No
  `public`/`visibility` column in P2** — the public library is deferred (Phase 9); everything is
  private.

### 4.3 AudioFile — table `audio_files` — **IMPLEMENTED — owns `storage_key`**
- **Required:** `id` PK UUID · `song_id` **FK→**`songs.id` · `purpose` enum
  (`original|vocals|background`) · `storage_key` str **U** (`uq_audio_files_storage_key`; internal
  object key) · `content_type` str (MIME, e.g. `audio/wav`) · `byte_size` BigInteger (bytes) ·
  `created_at` · `updated_at`.
- **Optional:** `checksum_sha256` str **null** (hex SHA-256, integrity) · `duration_seconds` Numeric
  **null** · `original_filename` str **null** (**sanitised** display metadata; meaningful for
  `purpose=original`; never a path).
- **FK / relationships:** belongs to `Song`; referenced by deferred `signed_url_grants`.
- **Unique / index:** **U** `(song_id, purpose)` (`uq_audio_files_song_id`) — at most one original,
  one vocals, one background per song; **U** `storage_key`; `IX` on `song_id`.
- **Security / privacy:** `storage_key` is **internal only** and **must not appear in any API/client
  schema** (enforced in P2-003). **No public URL field, no signed URL string field, no local
  filesystem path field, no checkpoint/model path field.** `content_type`/`byte_size`/`checksum`/
  `duration` are safe metadata. See §5, §6, §7.

### 4.4 SeparationJob — table `separation_jobs` — **IMPLEMENTED**
- **Required:** `id` PK UUID · `song_id` **FK→**`songs.id` · `status` enum
  (`queued|running|succeeded|failed|canceled`, default `queued`) · `created_at` · `updated_at`.
- **Optional:** `model_tier` enum **null** (`basic` only — **logical, never a path**) ·
  `error_message` str **null** (short failure text; **must not contain paths, secrets or
  `DATABASE_URL`**) · `started_at` **null** · `finished_at` **null**.
- **FK / relationships:** belongs to `Song`; referenced by `usage_events`.
- **Unique / index:** `IX` on `(song_id, created_at)`; `IX` on `status`. No uniqueness — a song may be
  re-processed, producing multiple jobs.
- **Security / privacy:** **`modelTier` logical only** — no checkpoint/model path, no
  `LOCAL_MODEL_ROOT`, no local filesystem path (§7). **`use_best_model` is not stored in P2**
  (deferred); if a later phase proves it necessary for local-prototype traceability it must be a
  **boolean**, never a path.

### 4.5 Tag — table `tags` — **IMPLEMENTED**
- **Required:** `id` PK UUID · `slug` str **U** (`uq_tags_slug`; stable machine key) · `name` str
  (display label) · `created_at` · `updated_at`.
- **FK / relationships:** `song_tags` (M:N `songs`).
- **Unique / index:** `uq_tags_slug`.
- **Security / privacy:** none special. Default tag values are seeded in **P2-004**, not here.

### 4.6 SongTag — table `song_tags` — **IMPLEMENTED (association)**
- **Required:** `song_id` **FK→**`songs.id` · `tag_id` **FK→**`tags.id` · `created_at`.
- **PK / unique:** **composite PK `(song_id, tag_id)`** (`pk_song_tags`) — this *is* the uniqueness
  ("a tag applies to a song at most once"). No surrogate id.
- **Index:** `IX` on `tag_id` (list songs by tag; `song_id` is covered by the PK's leading column).
- **Cascade:** when deletion is later implemented, `ON DELETE CASCADE` from `songs`/`tags` for safe
  association cleanup — **not wired in P2** (deletion not implemented).
- **Security / privacy:** none special.

### 4.7 UsageEvent — table `usage_events` — **IMPLEMENTED (append-only ledger)**
- **Required:** `id` PK UUID · `user_id` **FK→**`users.id` · `song_id` **FK→**`songs.id` ·
  `event_type` enum (`separation_succeeded`) · `created_at` (the event time; **no `updated_at`** —
  immutable ledger).
- **Optional:** `separation_job_id` **FK→**`separation_jobs.id` **null** (the job that finalised).
- **Unique / index (idempotency):** **U `(song_id, event_type)`** (`uq_usage_events_song_id`) — **at
  most one billable finalisation per song**. `IX` on `(user_id, created_at)`.
- **Behavioural rule (structural now, wired later):** a `separation_succeeded` row is written **only
  when** `SeparationJob.status = succeeded` **and** `Song.status = ready`. **Failed/canceled jobs
  create no billable usage** (`R-005`). The unique key is the `R-006` double-count guard. The
  increment/finalise *logic* lands in its authorized phase (P5/P7); Phase 2 defines only the table
  and constraint. See §8.
- **Security / privacy:** no secrets; append-only.

### 4.8 DailyUsage — table `daily_usage` — **IMPLEMENTED (per-user-per-day aggregate)**
- **Required:** `id` PK UUID · `user_id` **FK→**`users.id` · `usage_date` Date (UTC calendar date) ·
  `successful_count` Integer (default `0`) · `created_at` · `updated_at`.
- **Unique / index:** **U `(user_id, usage_date)`** (`uq_daily_usage_user_id`) — one row per user per
  day; `IX` on `usage_date` (optional reporting).
- **Relationship to UsageEvent:** `successful_count` is the **per-day rollup** of billable
  `UsageEvent`s for that user; it is derived from the ledger, with **no FK to a single UsageEvent**.
  The rollup/increment logic is P5/P7, not Phase 2.
- **Security / privacy:** none special.

### 4.9 Rating — table `ratings` — **DEFERRED (ratings / interaction phase)**
- **Contract:** `id` PK UUID · `user_id` **FK→**`users.id` · `song_id` **FK→**`songs.id` · `score`
  SmallInt (`CHECK 1..5`) · `created_at` · `updated_at` · **U `(user_id, song_id)`** — one rating per
  user per song.
- **Why deferred:** rating behaviour is not authorized in Phase 2 and depends on the
  public/interaction design; creating the table now would be speculative (`DEC-0002`, `R-009`).

### 4.10 Coupon — table `coupons` — **DEFERRED (billing phase)**
- **Contract:** `id` PK UUID · `code` str **U** (`uq_coupons_code`) · `status` enum
  (`active|disabled`) · `created_at` · `updated_at`. Discount value/type fields are a billing-phase
  decision.
- **Why deferred:** billing is an explicit **do-not-build** in Phase 2 (`02-product-scope`, AGENT.md).

### 4.11 CouponRedemption — table `coupon_redemptions` — **DEFERRED (billing phase, with Coupon)**
- **Contract:** `id` PK UUID · `coupon_id` **FK→**`coupons.id` · `user_id` **FK→**`users.id` ·
  `created_at` · **U `(coupon_id, user_id)`** — one redemption per user per coupon.
- **Why deferred:** depends on `Coupon` and billing behaviour.

### 4.12 SignedUrlGrant — table `signed_url_grants` — **DEFERRED (storage / signed-URL phase, P4/P6)**
- **Contract (audit metadata ONLY):** `id` PK UUID · `user_id` **FK→**`users.id` (subject granted) ·
  `audio_file_id` **FK→**`audio_files.id` (resource) · `purpose` enum (`download|listen`) ·
  `granted_at` · `expires_at` · `created_at` · `IX` on `(user_id, created_at)` and on `audio_file_id`.
- **Hard rule:** **never a `signed_url` / URL / token column.** The grant is an audit fact — subject,
  resource, purpose, grant time, expiry — the URL itself is a short-lived secret and is **not
  persisted** (`DEC-0003`, `06-security`).
- **Why deferred:** no signed URLs are issued in Phase 2; the grant row is written when a URL is
  actually granted.

### 4.13 ContentReport — table `content_reports` — **DEFERRED (public-library / moderation phase, P9)**
- **Contract:** `id` PK UUID · `reporter_user_id` **FK→**`users.id` · `song_id` **FK→**`songs.id`
  (target) · `status` enum (`open|reviewed|dismissed`, default `open`) · `reason` str · `created_at` ·
  `updated_at` · `IX` on `(song_id, status)`.
- **Why deferred:** the public library / reporting flow is not authorized in Phase 2; target rules
  depend on the public-library design.

### 4.14 AdminAuditEvent — table `admin_audit_events` — **DEFERRED (admin / RBAC phase, P10)**
- **Contract (append-only):** `id` PK UUID · `actor_user_id` **FK→**`users.id` · `event_type` enum
  (`url_grant|publish|admin_removal|account_deletion`) · `target_type` str · `target_id` UUID/str ·
  `created_at` · `IX` on `(actor_user_id, created_at)`.
- **Why deferred:** admin/RBAC scope is not authorized in Phase 2 (`R-008` — admin role must be scoped,
  not generic); exact fields depend on the admin design.

## 5. Storage reference contract

- **`AudioFile` is the sole owner of `storage_key`.** No other entity carries a storage reference.
- **No `bucket` or `provider` column.** The bucket/provider are environment/config concerns resolved
  at signed-URL time (local dev MinIO / prod S3-compatible per AGENT.md); persisting them would bake
  environment/bucket names into the DB. They stay **out of the data model**.
- **Present on `AudioFile`:** `content_type` (required), `byte_size` (required), `checksum_sha256`
  (optional), `duration_seconds` (optional), `original_filename` (optional, **sanitised**).
- **`storage_key` format (high level, provider-agnostic, opaque):** e.g.
  `song/<song_id>/<purpose>/<uuid>` — a logical internal key. **No real/private bucket name, no host,
  no absolute path, no operator-machine path.** The exact template is an implementation detail of the
  storage phase; the DB only stores the resulting opaque key.
- **`storage_key` is internal only** and **must not appear in any API/client schema** (P2-003).
- **No public URL fields. No signed URL string fields. No local filesystem path fields. No
  checkpoint/model path fields. No `LOCAL_MODEL_ROOT` in DB.**

## 6. Audio bytes prohibition

- **No audio bytes in DB.** The database stores **metadata only**; audio lives in private object storage.
- **No `LargeBinary` / `BYTEA` columns for audio** — on any entity, for any reason.
- **No base64 audio fields**, no inline audio payloads.
- Outputs (vocals, background) are referenced by **`AudioFile` metadata + `storage_key` only**.

## 7. Model / checkpoint path prohibition

- **No `checkpoint_path`.** **No `model_path`.** **No `local_model_root`.** **No local filesystem
  path column** on any entity.
- **No `LOCAL_MODEL_ROOT` value in DB** — it stays environment-only and out-of-band (`DEC-0004`).
- **`modelTier` is logical only:** it may be stored on `SeparationJob` as the string enum
  `model_tier` (`basic`), never as a path, filename or free checkpoint id (client never supplies it;
  `AGENT.md`, `R-003`).
- **`use_best_model` is not stored in P2.** If a later phase proves it necessary for local-prototype
  traceability, it must be a **boolean flag**, never a path.

## 8. Usage / idempotency contract

- **UsageEvent idempotency key:** **`UNIQUE(song_id, event_type)`**. Because every `Song` belongs to
  exactly one `User`, keying on `song_id` already scopes to the owner; this realises PHASE-02's
  "unique success finalization by song" and guards `R-006` (duplicate finaliser double-count).
- **Billable / final event:** **`separation_succeeded`**, written **once per song**, **only** when the
  `SeparationJob` reaches `succeeded` **and** the `Song` reaches `ready`.
- **DailyUsage uniqueness key:** **`UNIQUE(user_id, usage_date)`** — one aggregate row per user per
  UTC day.
- **UsageEvent ↔ DailyUsage:** `UsageEvent` is the authoritative **append-only ledger** of billable
  finalisations; `DailyUsage.successful_count` is a **derived per-day rollup** over that ledger. No
  direct row-to-row FK.
- **Failed / canceled jobs create no billable usage** (`R-005`), unless a future authorized decision
  states otherwise. Phase 2 encodes only the **structure** (unique constraints); the finalise/rollup
  **logic** is P5/P7.

## 9. Relationship graph

- **User → Song** — 1:N (`songs.user_id`). A song has exactly one owner.
- **Song → AudioFile** — 1:N (`audio_files.song_id`), with `UNIQUE(song_id, purpose)` bounding it to
  one `original` + one `vocals` + one `background`.
- **Song → SeparationJob** — 1:N (`separation_jobs.song_id`); a song may be re-processed.
- **Song ↔ Tag** — M:N through `SongTag` (composite PK `(song_id, tag_id)`).
- **Song → Rating** *(deferred)* — 1:N, `UNIQUE(user_id, song_id)`.
- **User → DailyUsage** — 1:N, `UNIQUE(user_id, usage_date)`.
- **UsageEvent → User / Song / SeparationJob** — N:1 each (`user_id`, `song_id` required;
  `separation_job_id` optional).
- **User → CouponRedemption** and **Coupon → CouponRedemption** *(deferred)* — N:1 each,
  `UNIQUE(coupon_id, user_id)`.
- **SignedUrlGrant → User / AudioFile** *(deferred)* — N:1 each; audit metadata only, never the URL.
- **ContentReport → reporter `User` / target `Song`** *(deferred)* — N:1 each.
- **AdminAuditEvent → actor `User` / target (`target_type` + `target_id`)** *(deferred)* — N:1 actor;
  target is a typed reference pair, not a hard FK.

## 10. Constraints / indexes (summary — deterministic names per DEC-0005)

| Table | Unique | Index |
|---|---|---|
| `users` | `uq_users_email` | — |
| `songs` | — | `(user_id, created_at)`, `status` |
| `audio_files` | `(song_id, purpose)` (`uq_audio_files_song_id`), `storage_key` (`uq_audio_files_storage_key`) | `song_id` |
| `separation_jobs` | — | `(song_id, created_at)`, `status` |
| `tags` | `uq_tags_slug` | — |
| `song_tags` | composite **PK** `(song_id, tag_id)` | `tag_id` |
| `usage_events` | **`(song_id, event_type)`** (idempotency) | `(user_id, created_at)` |
| `daily_usage` | **`(user_id, usage_date)`** | `usage_date` |
| `ratings` *(deferred)* | `(user_id, song_id)` | — |
| `coupons` *(deferred)* | `uq_coupons_code` | — |
| `coupon_redemptions` *(deferred)* | `(coupon_id, user_id)` | — |
| `signed_url_grants` *(deferred)* | — | `(user_id, created_at)`, `audio_file_id` |
| `content_reports` *(deferred)* | — | `(song_id, status)` |
| `admin_audit_events` *(deferred)* | — | `(actor_user_id, created_at)` |

Every `CHECK` for a §3-enums column is given an explicit name so the DEC-0005 `ck` pattern produces a
deterministic constraint name (e.g. `ck_separation_jobs_status_allowed`).

## 11. Deferred decisions / explicit notes

- The **six deferred entities** (§4.9–§4.14) have their contract fixed here; only table creation is
  deferred to the named phase. No core upload/result/usage entity is left undefined: `User`, `Song`,
  `AudioFile`, `SeparationJob`, `UsageEvent`, `DailyUsage` are all fully specified and implemented in
  P2-002, plus `Tag`/`SongTag` for organisation and P2-004 seeding.
- **Authentication credential fields** on `User` are intentionally **not** designed here — they belong
  to Phase 3 (Auth). Phase 2 needs only `id` + `email` + `status` for ownership.
- **Account deletion / retention / tombstone** behaviour (cascade semantics) remains open (OD-007,
  Phase 11); Phase 2 wires no cascades.
- **Discount/value semantics** for `Coupon`, and **admin field detail** for `AdminAuditEvent`, are
  left to their billing/admin phases; only the minimal audited shape is fixed.

## 12. P2-002 implementation contract

**P2-002 is READY for implementation — scoped to the 8 implemented entities** in §2
(`User`, `Song`, `AudioFile`, `SeparationJob`, `Tag`, `SongTag`, `UsageEvent`, `DailyUsage`), their
enums (§3-enums), relationships (§9), constraints/indexes (§10) and the initial Alembic migration for
exactly those tables.

**The 6 deferred entities are explicitly out of P2-002 scope** (their tables are created in their
approved phases, using the contract fixed here). This is a deliberate **core-entities-only**
recommendation: it keeps P2-002 minimal and avoids speculative billing/admin/public-library/signed-URL
schema ahead of the decisions that govern their behaviour.

P2-002 remains **not authorized to execute** until Nadav reviews this record and issues an explicit
implementation authorization (§14). When authorized, P2-002 is now a **mechanical** task — every
field, state, key and index it needs is decided above; it must **not** re-decide any of them, add
entities, or pull deferred tables forward.

## 13. Test contract (required when P2-002 is implemented)

Supersedes the earlier "model creation / migration" placeholder. All must pass:

1. **Expected tables** — `Base.metadata` contains exactly the 8 implemented tables (no deferred table,
   no extra table).
2. **Expected columns** — each implemented entity has exactly the fields in §4 (name + nullability).
3. **Enum values** — each enum column allows exactly the §3-enums set (asserted against the `CHECK`),
   not free-form strings.
4. **Relationships** — the FKs in §9 exist and point at the right tables.
5. **Uniqueness constraints** — `users.email`; `audio_files (song_id, purpose)` and `storage_key`;
   `tags.slug`; `song_tags` composite PK; **`usage_events (song_id, event_type)`**;
   **`daily_usage (user_id, usage_date)`**.
6. **Indexes** — the §10 indexes exist with DEC-0005-convention names.
7. **No audio-bytes columns** — assert **no `LargeBinary` / `BYTEA`** column anywhere in
   `Base.metadata`.
8. **No checkpoint/model/local-path columns** — assert no column name or type stores a
   checkpoint/model/local filesystem path (no `checkpoint_path`, `model_path`, `local_model_root`,
   `local_path`).
9. **No signed-URL-string columns** — assert no `signed_url` / URL-token column on any entity
   (including `signed_url_grants` once created).
10. **No public-URL columns** — assert no public/permanent object-URL column.
11. **`storage_key` internal only** — present on `AudioFile`; a companion P2-003 schema test proves it
    is not serialised into any API/client schema.
12. **`modelTier` logical only** — `SeparationJob.model_tier` is a string enum (`basic`), never a path.
13. **UsageEvent idempotency uniqueness** — the `(song_id, event_type)` unique constraint exists.
14. **DailyUsage uniqueness** — the `(user_id, usage_date)` unique constraint exists.
15. **Alembic compatibility** — the initial migration builds the 8 tables; autogenerate is stable
    (deterministic DEC-0005 names, no drift on a second autogenerate).
16. **Existing P2-001 tests still pass** — DB base/session/config/Alembic-scaffold suite unaffected.
17. **Phase 0/1 regressions still pass** — `/health`, config, worker startup and the AI-boundary
    lazy-import test are unaffected.

## 14. Source-of-truth note & authorization boundary

- **DEC-0006 and the repo-local `docs/tasks/phase-2/P2-002-domain-models.md` are the active
  implementation contract for P2-002.** Where the read-only Dev Pack
  (`stemspace-dev-pack-v0.1/*`) differs, these repo-local docs win; the Dev Pack remains authoritative
  for anything they do not supersede (project boundaries, `AGENT.md`, evidence template).
- **Authorization boundary:** DEC-0006 closes the *decisions*; it authorizes **no** code. P2-002
  implementation begins only after **Nadav** reviews this record and issues an explicit implementation
  authorization. **P2-003 onward remain out of scope** and unauthorized.

## Rationale

The P2-002 readiness gate reported BLOCKED because the shared data contract — fields, states,
uniqueness/idempotency keys and `storage_key` shape — was undefined, which would have forced the code
agent to invent product and architecture decisions (`docs/coding-rules.md` §9). Deciding them here, in
an authority-owned record grounded in the pack's own risk register (`R-004`/`R-005`/`R-006`) and
security rules, converts P2-002 into a mechanical, testable task, and fixes the shared data foundation
that gates P3–P8 **before** it is written — far cheaper than migrating away from it later.
