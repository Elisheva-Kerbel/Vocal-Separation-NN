# DEC-0007 — Phase 2 Pydantic schema contract (P2-003)

Status: **Approved for P2-003 planning / pending Nadav implementation authorization.**
Not an implementation authorization. Not production-approved. No public users. No commercial approval.

Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2 · Recorded by: DEC-0007 schema-contract work
Relates to: `DEC-0002` (minimal code), `DEC-0003` (private storage only), `DEC-0004` (local model prototype),
`DEC-0005` (DB base / session / Pydantic-is-the-schema-layer), `DEC-0006` (Phase 2 domain data contract),
`docs/coding-rules.md`, `docs/tasks/phase-2/P2-003-pydantic-schemas-no-storage-key-leak.md`
Baseline (read-only historical): `stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-003-pydantic-schemas-no-storage-key-leak.md`,
`stemspace-dev-pack-v0.1/packages/PKG-P2-backend-domain-db-skeleton.md`,
`stemspace-dev-pack-v0.1/06-security-permissions-and-secrets.md`,
`stemspace-dev-pack-v0.1/07-testing-and-evidence-strategy.md`, `stemspace-dev-pack-v0.1/09-risk-register.md`

> This record closes the schema-boundary decisions that made the P2-003 readiness gate report
> **BLOCKED** (schema class list, read/create/update direction, per-entity inclusion, Pydantic v2
> pin, and the `app/schemas`-absent guardrail-test update). It defines the **positive** schema
> contract so P2-003 can later be implemented **mechanically**, without the code agent inventing a
> schema or privacy boundary (`docs/coding-rules.md` §9). It authorizes **no** code, **no** schemas,
> **no** dependency install, **no** route. P2-003 begins only after Nadav reviews this record and
> issues an explicit implementation authorization (see §12).

## 1. Decision

Fix the Phase 2 **external Pydantic schema contract**: the exact set of read-only client-facing
schema classes for the P2-002 core entities, their exact field sets, the forbidden-field boundary
that keeps private storage state from crossing the API line, the Pydantic version/style, and the one
permitted change to an existing P2-002 guardrail test. This is the smallest schema surface sufficient
to discharge risk **R-004** ("storage key leaks to frontend", High) by proving **DB model ≠ API
schema** (PKG-P2; `DEC-0005` §3: "Pydantic remains the schema layer, not the DB layer").

It adds **no** create/update schemas, **no** admin schemas, **no** deferred-entity schemas, **no**
routes, **no** service layer, and **no** dependency other than an explicit Pydantic v2 pin.

## 2. Schema scope — read-only only

P2-003 creates **read-only** Pydantic schemas only. Explicitly **not** in scope:

- **No create schemas** (`UserCreate`, `SongCreate`, `AudioFileCreate`, `SeparationJobCreate`,
  `TagCreate`, …).
- **No update schemas** (`UserUpdate`, `SongUpdate`, …).
- **No upload / request / input schemas.**
- **No admin schemas.**
- **No deferred-entity schemas** (§4).
- **No API routes, no service layer, no repository layer.**

Rationale: P2-003 has no route, upload flow or service that would consume an input schema. A
create/update schema with no consumer is speculative scaffolding, forbidden by `docs/coding-rules.md`
§1 ("Add a contract/interface only when another component actually consumes it") and `DEC-0002`.
Create/update schemas are **deferred** to the phase that adds API routes or the upload flow.

## 3. Allowed schema classes (exact, closed)

P2-003 defines **exactly** these six classes — no more, no fewer:

1. `UserRead`
2. `SongRead`
3. `AudioFileRead`
4. `SeparationJobRead`
5. `TagRead`
6. `CommonMessage`

**Do not add any additional schema class** unless a future decision record amends this list.

## 4. Entities that get NO schema in P2-003

No schema is created for the following. Each is internal, deferred, or has no current client/API
consumer; creating one would be speculative (`DEC-0002`, `R-009`) or would pull deferred work forward.

- **Core, but internal / no client consumer:** `SongTag` (association), `UsageEvent` (append-only
  billable ledger — admin/internal), `DailyUsage` (per-day aggregate — internal/admin).
- **Deferred (tables not created in P2-002; contract in DEC-0006 §4.9–§4.14):** `Rating`, `Coupon`,
  `CouponRedemption`, `SignedUrlGrant`, `ContentReport`, `AdminAuditEvent`.

If any of these later needs a schema, that is a **future decision**, not a P2-003 action. In
particular, `SignedUrlGrant` must **never** get a schema carrying a signed-URL / URL / token field
(`DEC-0005` §9, `DEC-0006` §4.12).

## 5. Exact field contract per class

Fields are taken verbatim from the P2-002 model columns in `backend/app/db/models.py`
(`DEC-0006` §4). Read schemas deliberately expose a **safe subset** — omission of a column
(e.g. `AudioFile.storage_key`, or a table's `updated_at`) is intentional, not an oversight.

### 5.1 `UserRead`
- `id`
- `email`
- `status`
- `created_at`
- `updated_at`

No password / auth-credential fields (none exist on the model; authentication is Phase 3 —
`DEC-0006` §4.1, §11).

### 5.2 `SongRead`
- `id`
- `user_id`
- `title`
- `status`
- `created_at`
- `updated_at`

No storage reference (the model carries none — `DEC-0006` §4.2). No `public`/`visibility` field.

### 5.3 `AudioFileRead`  — the R-004 proof schema (§7)
- `id`
- `song_id`
- `purpose`
- `content_type`
- `byte_size`
- `checksum_sha256`
- `duration_seconds`
- `original_filename`
- `created_at`

**Deliberately excludes `storage_key`** and every other private field in §8. Exposes only safe audio
metadata (`DEC-0006` §5). `updated_at` is intentionally not exposed.

### 5.4 `SeparationJobRead`
- `id`
- `song_id`
- `status`
- `model_tier`
- `error_message`
- `started_at`
- `finished_at`
- `created_at`
- `updated_at`

`model_tier` is a **logical enum only** (`basic`), never a checkpoint/model/local path
(`DEC-0006` §4.4, §7). `error_message` is short failure text and must never carry a path, secret or
`DATABASE_URL`.

### 5.5 `TagRead`
- `id`
- `slug`
- `name`
- `created_at`

`updated_at` is intentionally not exposed.

### 5.6 `CommonMessage`
- `message`

A **minimal** message wrapper only. **Do not** expand it into a pagination envelope, error/problem
-details envelope, or metadata envelope — those arrive with the phase that needs them (§ decision 12
below).

## 6. Pydantic version and style

- **Dependency:** P2-003 may add an **explicit direct** dependency pin to `backend/requirements.txt`:
  **`pydantic>=2,<3`** — and **nothing else**. Pydantic is already available transitively via
  `fastapi>=0.115,<1.0`; the explicit pin exists only to make the **v2** resolution deterministic and
  to declare the schema layer as a first-class dependency. It must not pull `redis`, `celery`,
  `boto3`, `minio`, any storage/queue client, or any other package.
- **Style — Pydantic v2 idioms only:** `model_config`, `model_fields`, `model_dump()`.
- **Forbidden Pydantic v1 idioms:** `__fields__`, `.dict()`, `orm_mode`, `Config`-class `orm_mode`,
  `from_orm`-style implicit passthrough. External schemas name their fields explicitly; no unreviewed
  ORM passthrough (`DEC-0005` §3, P2-003 guardrails).

## 7. `AudioFileRead` leak-prevention purpose

`AudioFileRead` is **required** in P2-003 precisely because `AudioFile` is the sole owner of
`storage_key` (`DEC-0006` §4.3, §5) and is therefore the entity R-004 is about. Its role in P2-003 is
to be the concrete, tested proof that a client can receive an audio file's **safe metadata**
(`purpose`, `content_type`, `byte_size`, `checksum_sha256`, `duration_seconds`, `original_filename`,
`created_at`) **without** ever receiving `storage_key`, a bucket/provider, a signed URL, a public URL,
or any local/model path. Omitting `AudioFileRead` would leave R-004 undischarged; that is why it is in
the class list despite the pack's original file list naming only user/song/job.

## 8. Forbidden fields (binding on every P2-003 schema)

No P2-003 schema may include any of the following — not as a field, alias, example, nested field,
inherited field, or debug/error payload:

`storage_key`, `checkpoint_path`, `model_path`, `local_model_root`, `LOCAL_MODEL_ROOT`, `local_path`,
`path`, `signed_url`, `public_url`, `url`, `bucket`, `provider`, `database_url`, `password`, `secret`,
`token`, `audio_bytes`, `base64_audio`, `binary_audio`, `traceback`, `internal_error`.

Restating the canonical security rules (`DEC-0005` §9, `DEC-0006` §5–§7) at the schema boundary:

- `storage_key` must not be exposed in any client/API schema.
- No checkpoint / model / local filesystem path, and no `LOCAL_MODEL_ROOT`, in any schema.
- No signed-URL string is serialized or round-tripped back into storage.
- No public bucket URL and no public/permanent object URL.
- No `DATABASE_URL` / password / secret / token in any schema, example, validation error or response.
- No audio bytes and no base64 audio in any schema.
- Validation errors must be **safe** — no secrets, paths, storage keys, connection strings or
  tracebacks echoed back to the client.

## 9. No internal storage-key schema

P2-003 creates **no** internal schema that exposes `storage_key` — not even one marked "internal
only". There is no consumer for it in this phase, so none is built (`DEC-0002`). If an internal
storage-key schema is ever genuinely needed, it is a **future decision**, and it must still never be
returned across the API/client boundary.

## 10. Permitted change to an existing P2-002 guardrail test

The P2-002 regression test `backend/tests/db/test_domain_security_guardrails.py` currently asserts
that `backend/app/schemas/` **does not exist**
(`test_no_api_schema_or_service_surface_created`). Creating the P2-003 schema package would break
that passing test. P2-003 is therefore **explicitly permitted** to update that single assertion so it:

- **allows** `backend/app/schemas/`, **but**
- **still forbids** `backend/app/api/`, `backend/app/routers/`, `backend/app/services/`, and any
  route / queue / storage / AI-integration surface.

No other change to that test file, and no relaxation of any other guardrail, is authorized.

## 11. Test contract (required when P2-003 is implemented)

All must pass; assertions inspect **actual `model_fields`** (Pydantic v2), not only hardcoded denylist
strings, so a newly added internal field fails the test rather than silently passing:

1. **Expected classes exist** — exactly `UserRead`, `SongRead`, `AudioFileRead`, `SeparationJobRead`,
   `TagRead`, `CommonMessage` (§3), and no other schema class.
2. **Exact field sets** — each class's `model_fields` **equals** its §5 field list exactly (no missing
   field, no extra field).
3. **Pydantic v2 style** — schemas use v2 idioms (`model_config` / `model_fields` / `model_dump`); no
   v1 idiom (`__fields__`, `.dict()`, `orm_mode`).
4. **Serialization excludes forbidden fields** — `model_dump()` of representative data for every schema
   omits every §8 field.
5. **`storage_key` absent** from every schema's field set and serialized output.
6. **All §8 forbidden fields absent** from every schema (field-set inspection + serialization).
7. **`AudioFileRead` proves safe exposure** — it carries exactly its §5.3 safe metadata and **no**
   `storage_key` / bucket / provider / signed URL / public URL / local path.
8. **No create/update schemas exist** (no `*Create` / `*Update` schema class).
9. **No deferred-entity schemas exist** (none for the §4 entities).
10. **No API routes added** — `backend/app/api/`, `backend/app/routers/`, `backend/app/services/` do
    not exist; no route/queue/storage/AI surface is introduced.
11. **Existing P2-001 / P2-002 DB tests still pass** — including the amended
    `test_domain_security_guardrails.py` (§10).
12. **Phase 0/1 regressions still pass** — `/health`, config, worker startup, and the AI-boundary
    lazy-import test are unaffected.

`07-testing-and-evidence-strategy.md` requires "proof that `storage_key` is not exposed in API
schemas" as Phase 2 evidence; tests 4–7 are that proof, and PKG-P2 makes them a contract test future
API providers must pass before any UI consumes the API.

## 12. Out of scope / deferred

- **Create/update/input/admin schemas** — deferred to the route/upload phase (§2).
- **Deferred-entity schemas** — created in each entity's approved phase, if ever (§4).
- **`CommonMessage` expansion** — no pagination, error envelope, problem-details or metadata envelope
  in P2-003; added only when a later phase requires it.
- **API routes, service layer, upload flow, queue/Redis/Celery, storage client/MinIO/S3, signed-URL
  generation, AI integration, frontend, worker changes, production DB/migrations, auth/billing/admin/
  public library/resumable upload/extra stems** — all remain out of scope and unauthorized.
- **No dependency other than `pydantic>=2,<3`** may be added.

## 13. Source-of-truth note & authorization boundary

- **DEC-0007 and the repo-local `docs/tasks/phase-2/P2-003-pydantic-schemas-no-storage-key-leak.md`
  are the active implementation contract for P2-003.** Where the read-only Dev Pack
  (`stemspace-dev-pack-v0.1/*`) differs, these repo-local docs win; the Dev Pack remains authoritative
  for anything they do not supersede (project boundaries, `AGENT.md`, evidence template).
- **Authorization boundary:** DEC-0007 closes the *decisions*; it authorizes **no** code, schema,
  dependency install or route. P2-003 implementation begins only after **Nadav** reviews this record
  and issues an explicit implementation authorization. **P2-004 onward remain out of scope** and
  unauthorized.

## Rationale

The P2-003 readiness gate reported BLOCKED because the schema-class contract — which classes exist,
their direction (read vs create/update), which entities are client-facing, the Pydantic version/style,
and the one guardrail-test that assumes `app/schemas` never exists — was undefined, which would have
forced the code agent to invent the schema and privacy boundary (`docs/coding-rules.md` §9). The
field-level *privacy* rules were already fixed (`DEC-0005` §9, `DEC-0006` §5–§7); this record fixes the
remaining *class/direction/scope* contract on top of them. Deciding these in an authority-owned record
converts P2-003 into a mechanical, testable task that discharges R-004, and fixes the external contract
that P3+ UI will consume **before** it is written — far cheaper than reshaping it later.
