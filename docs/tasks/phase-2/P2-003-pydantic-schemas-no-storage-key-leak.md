# P2-003 — Pydantic Schemas and No Storage Key Leak

Status: **BLOCKED — guardrails only. Not authorized. Depends on P2-002, which is itself blocked.**
Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2
Depends on: P2-002 complete (authorized + accepted) · `docs/decisions/DEC-0003`, `DEC-0005`
Baseline: `stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-003-pydantic-schemas-no-storage-key-leak.md`

> **Guardrails only. Do not implement.** This document sharpens the private-field boundary before any
> external schema exists. It authorizes no schemas and no code.

## Purpose of this task (when later authorized)

Create the **external** API schemas — the client-facing contract — such that no internal or private
storage field can cross the boundary. **DB model ≠ API schema** (PKG-P2). Pydantic is the schema
layer, not the DB layer (`DEC-0005` §3).

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

1. **Schema serialization leak test** (`backend/tests/schemas/test_no_storage_key_leak.py`, per the
   source task) — serialize every external schema and assert **`storage_key` is absent** from the
   output.
2. **Private-field leak test** — assert no external schema leaks internal/private storage fields
   generally: storage keys, internal file refs, checkpoint/model/local paths, or signed URL strings.
   Prefer an assertion over the schema's **actual field set**, so a *newly added* internal field
   fails the test instead of silently passing a hardcoded denylist.
3. **No public URL test** — assert no schema emits a public or permanent object URL.
4. **Safe validation errors** — assert error output carries no secrets, paths, storage keys or
   connection strings.

`07-testing-and-evidence-strategy.md` requires "proof that `storage_key` is not exposed in API
schemas" as **Phase 2 evidence** — these tests are that proof, and PKG-P2 makes them a contract test
that future API providers must pass before any UI consumes the API.

## Out of scope

API routes/endpoints; services; upload; queue; Redis; storage client; **signed URL generation**; AI
integration; frontend; worker processing; production DB; auth/billing/admin/public library.

## Stop gate

Do not start. P2-003 begins only after P2-002 is accepted and an explicit prompt authorizes it.
