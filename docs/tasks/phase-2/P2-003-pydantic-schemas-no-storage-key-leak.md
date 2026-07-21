# P2-003 — Pydantic Schemas and No Storage Key Leak

Status: **Contract closed by DEC-0007 — pending Nadav implementation authorization. Do not implement yet.**
Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2
Depends on: P2-002 complete (accepted) · `docs/decisions/DEC-0003`, `DEC-0005`, `DEC-0006` ·
**`docs/decisions/DEC-0007-p2-schema-contract.md` (schema class/field/forbidden-field contract)**
Baseline: `stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-003-pydantic-schemas-no-storage-key-leak.md`

> **Contract closed, not yet authorized.** The schema-boundary decisions that previously blocked
> P2-003 (class list, read/create/update direction, entity inclusion, Pydantic v2 pin, and the
> `app/schemas`-absent guardrail-test update) are now **resolved by
> `docs/decisions/DEC-0007-p2-schema-contract.md`**. This document plus DEC-0007 are the active
> implementation contract. Implementation still requires an **explicit Nadav authorization** — do not
> write schemas or code until it is issued. When authorized, implement **exactly** the DEC-0007
> contract; the code agent must **not** re-decide any of it (`docs/coding-rules.md` §9).

## Closed decisions (see DEC-0007)

The schema-boundary decisions that previously left this task BLOCKED are now fixed in
`docs/decisions/DEC-0007-p2-schema-contract.md`; the code agent must **not** re-decide them:

1. **Scope** — **read-only schemas only.** No create schemas, no update schemas, no upload/request
   schemas, no admin schemas, no deferred-entity schemas, no routes, no service layer (DEC-0007 §2).
2. **Exact class list** — exactly `UserRead`, `SongRead`, `AudioFileRead`, `SeparationJobRead`,
   `TagRead`, `CommonMessage`; no other schema class (DEC-0007 §3).
3. **No schemas** for `SongTag`, `UsageEvent`, `DailyUsage`, or any deferred entity (`Rating`,
   `Coupon`, `CouponRedemption`, `SignedUrlGrant`, `ContentReport`, `AdminAuditEvent`) (DEC-0007 §4).
4. **Exact field sets** per class are fixed in DEC-0007 §5.
5. **Pydantic v2 only** — `model_config` / `model_fields` / `model_dump`; never `__fields__`, `.dict()`
   or `orm_mode`. P2-003 may add the explicit pin **`pydantic>=2,<3`** to `backend/requirements.txt`
   **and nothing else** (DEC-0007 §6).
6. **`AudioFileRead` is required** as the R-004 proof schema — safe audio metadata only, never
   `storage_key` (DEC-0007 §7, §10).
7. **Forbidden-field list** is fixed in DEC-0007 §8.
8. **Guardrail-test update is permitted** — see the "Files P2-003 may create/change" note below and
   DEC-0007 §10.

**Rule:** implement exactly the DEC-0007 contract. Do not invent schema classes or fields, do not add
create/update schemas, do not add deferred-entity schemas, and do not add any dependency other than
`pydantic>=2,<3` (`docs/coding-rules.md` §9).

## Files P2-003 may create / change (when later authorized)

- `backend/app/schemas/__init__.py`, `backend/app/schemas/common.py`, `backend/app/schemas/core.py`
  (or a minimal equivalent split — prefer the smallest clear structure; do not over-split).
- `backend/requirements.txt` — **only** to add `pydantic>=2,<3` as an explicit pin (Pydantic is
  already available transitively via FastAPI; the pin makes the v2 resolution deterministic).
- `backend/tests/schemas/test_no_storage_key_leak.py` (and any sibling schema tests).
- `backend/tests/db/test_domain_security_guardrails.py` — **only** the single assertion that currently
  requires `backend/app/schemas/` to be absent: update it to **allow** `backend/app/schemas/` while
  **still forbidding** `backend/app/api/`, `backend/app/routers/`, `backend/app/services/` and any
  route/queue/storage/AI surface (DEC-0007 §10). No other change to that file.

## Purpose of this task (when later authorized)

Create the **external, read-only** API schemas — the client-facing contract — such that no internal or
private storage field can cross the boundary. **DB model ≠ API schema** (PKG-P2). Pydantic is the
schema layer, not the DB layer (`DEC-0005` §3).

This is the task that discharges risk **R-004** ("Storage key leaks to frontend", severity High).

## Security guardrails (binding)

- **`storage_key` must not be exposed** in any client/API schema — not as a field, not as an alias,
  not in an example, not in a debug/error payload, and not via a nested or inherited model.
- **Checkpoint / local model paths must never be exposed.** No checkpoint path, model path, weights
  filename, operator-machine filesystem path or `LOCAL_MODEL_ROOT` value appears in any schema,
  response, error, log or metric (`DEC-0004` §9). A client sends at most a logical `modelTier` and
  **never** a checkpoint path, filename or id (`AGENT.md`, P1-002).
- **The signed URL string must not be persisted or serialized** as stored state. Signed URLs are
  short-lived credentials minted per authorized request in their own later phase; **no signed URL
  string in DB**, and no schema field that round-trips one back into storage.
- **No public storage URLs** — no public bucket URL, no public object URL, no permanent file URL in
  any schema.
- **Do not expose DB models directly.** No `Model.from_orm`-style passthrough of an entity whose
  fields have not been explicitly reviewed; external schemas name their fields explicitly.
- **`DATABASE_URL` must not be logged or echoed** — never in a validation error, a schema example or
  an error response.
- Validation errors must be **safe**: they must not echo secrets, internal paths, storage keys or
  connection strings back to the client.
- **no audio bytes in DB** and no audio bytes in schemas — audio moves through private storage, not
  through the API contract as inline bytes.
- **No routes.** P2-003 adds schemas and schema tests only.

## Required tests when implemented

The full, closed test contract is **DEC-0007 §11**; the code agent must satisfy it exactly. In
summary, all of the following must pass, inspecting **actual `model_fields`** (Pydantic v2) rather
than only hardcoded denylist strings:

1. **Expected classes exist** — exactly `UserRead`, `SongRead`, `AudioFileRead`, `SeparationJobRead`,
   `TagRead`, `CommonMessage` (DEC-0007 §3), and no other schema class.
2. **Exact field sets** — each class's `model_fields` equals its DEC-0007 §5 field list exactly (no
   missing field, no extra field).
3. **Pydantic v2 style** — schemas use `model_config` / `model_fields` / `model_dump`; no `__fields__`,
   `.dict()` or `orm_mode`.
4. **Serialization excludes forbidden fields** — `model_dump()` of representative data for every schema
   omits every DEC-0007 §8 field.
5. **`storage_key` absent** from every schema's field set and serialized output
   (`backend/tests/schemas/test_no_storage_key_leak.py`, per the source task).
6. **All forbidden fields absent** — the full DEC-0007 §8 list, via field-set inspection and
   serialization.
7. **`AudioFileRead` proves safe exposure** — exactly its DEC-0007 §5.3 metadata and no `storage_key` /
   bucket / provider / signed URL / public URL / local path.
8. **No create/update schemas exist**; **no deferred-entity schemas exist**; **no API routes added**
   (`backend/app/api/`, `backend/app/routers/`, `backend/app/services/` absent).
9. **Existing P2-001 / P2-002 DB tests still pass** — including the amended
   `test_domain_security_guardrails.py` (which now allows `backend/app/schemas/` but still forbids
   `api`/`routers`/`services`; DEC-0007 §10).
10. **Phase 0/1 regressions still pass** — `/health`, config, worker startup and the AI-boundary
    lazy-import test are unaffected.

`07-testing-and-evidence-strategy.md` requires "proof that `storage_key` is not exposed in API
schemas" as **Phase 2 evidence** — these tests are that proof, and PKG-P2 makes them a contract test
that future API providers must pass before any UI consumes the API.

## Out of scope

Create/update/input/admin/deferred-entity schemas; any dependency other than `pydantic>=2,<3`; API
routes/endpoints; services; upload; queue; Redis; storage client; **signed URL generation**; AI
integration; frontend; worker processing; production DB; auth/billing/admin/public library. Do not
expand `CommonMessage` beyond a minimal message wrapper (DEC-0007 §5.6, §12).

## Stop gate

Do not start. The schema contract is closed by `docs/decisions/DEC-0007-p2-schema-contract.md`, but
P2-003 implementation begins only after P2-002 is accepted (it is) **and** an explicit Nadav
authorization for P2-003 is issued. When authorized, implement exactly the DEC-0007 contract, run the
test contract above, return the evidence report, and stop; do not continue to P2-004.
