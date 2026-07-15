# P2-004 — Seed Tags and DB Tests

Status: **BLOCKED — guardrails only. Not authorized. Depends on P2-002, which is itself blocked.**
Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2
Depends on: P2-002 complete (authorized + accepted) · `docs/decisions/DEC-0005` · **open decisions below**
Baseline: `stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-004-seed-tags-and-db-tests.md`

> **Guardrails only. Do not implement.** This document aligns the required DB tests and closes the
> "invent a key" escape hatch before anyone writes a constraint. It authorizes no script, no tests
> and no code.

## Blocking open decisions

1. **UsageEvent uniqueness / idempotency key.** `PHASE-02` requires "UsageEvent supports unique
   success finalization by song"; `R-006` requires "idempotency and unique success constraints";
   PKG-P2 requires the strategy be "compatible with Phase 7". None of these state the **key**:
   `(song_id)` vs `(user_id, song_id)` vs `(user_id, song_id, date)`.
2. **The success/Ready state value** the constraint keys on — undefined until the Song /
   SeparationJob state decision closes (see `P2-002-domain-models.md`). `R-005` requires that failed
   processing never counts toward quota, so the constraint must key on a *specific* success state
   that does not yet exist.
3. **Default tag taxonomy.** Not supplied.

**Rule — this closes an escape hatch.** The source task permits "UsageEvent uniqueness support is
test-covered **or blocker documented**" and "add unapproved tag taxonomy if not supplied: use
placeholder/minimal seed **or mark blocker**". When state/idempotency decisions are missing, the
task **must stop and report a blocker rather than inventing keys**. A guessed uniqueness key is worse
than no key: it silently encodes a quota rule that Product never approved, into a constraint that
Phase 7 then inherits. Do not choose the lenient branch of that "or" to keep moving.

For tags specifically: a **minimal placeholder seed is acceptable** if and only if it is clearly
labelled as placeholder and carries no product-taxonomy claim. Uniqueness keys have **no** equivalent
placeholder — report the blocker.

## Required DB tests when implemented

1. **Seed idempotency test** — running the seed twice produces the same rows, no duplicates, no
   error. Safe duplicate-seed behavior.
2. **UsageEvent uniqueness / idempotency test** — once the key is approved, prove the DB **rejects a
   duplicate success finalization** for the same key (a real constraint violation, not
   application-level checking). This is the evidence Phase 7 quota finalization depends on, and it
   guards `R-006` (duplicate worker/finalizer double-counts usage).
3. **Failed-processing test** — prove a non-success job does **not** create a finalized usage record
   (`R-005`).
4. **Deterministic constraint naming** — the unique constraint's name follows the DEC-0005 naming
   convention (`uq_%(table_name)s_%(column_0_name)s`), not a backend-generated name.
5. **Automated no-audio-bytes-in-DB test** — see `P2-002-domain-models.md`; **no audio bytes in DB**,
   no `LargeBinary` / `BYTEA` audio columns.
6. **Phase 0/1 regression tests still pass.**

## Security guardrails (binding)

- **no audio bytes in DB** — seeds included; no seed inserts binary audio.
- **no checkpoint/model/local filesystem paths in DB** — no seed, default or fixture writes a
  checkpoint path, model path or operator-machine path. **No `LOCAL_MODEL_ROOT` value in DB.**
- **no signed URL string in DB** — no seed or test fixture persists one.
- **`storage_key` must not be exposed** in client/API schemas; seeds and tests must not print storage
  keys into committed output.
- **No public storage URLs** in seeds or fixtures.
- **`DATABASE_URL` must not be logged or echoed** — not by the seed script, not in test output, not
  in a connection-failure message.
- Seeds use **local Compose Postgres only**; **no production DB**. No real secrets; placeholders only.
- No tag UI, no public library, no admin moderation (`PKG-P2` "Do Not Build").

## Out of scope

Tag UI; public library; admin; API routes; upload; queue; Redis; storage client; signed URL
generation; AI integration; frontend; worker processing; production DB; production migrations.

## Stop gate

Do not start. P2-004 begins only after P2-002 is accepted, the blocking decisions above are recorded,
and an explicit prompt authorizes it. If prompted while the uniqueness key is undecided: **report a
blocker, invent nothing.**
