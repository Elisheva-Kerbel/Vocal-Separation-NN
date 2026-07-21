# P2-004 — Seed Tags and DB Tests

Status: **Contract closed by DEC-0008 — pending Nadav implementation authorization. Do not implement yet.**
Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2
Depends on: P2-002 complete (accepted) · P2-003 complete (accepted) · `docs/decisions/DEC-0005`,
`DEC-0006` · **`docs/decisions/DEC-0008-p2-seed-tags-and-db-test-policy.md` (seed taxonomy + DB-test
execution policy)**
Baseline: `stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-004-seed-tags-and-db-tests.md`

> **Contract closed, not yet authorized.** The two decisions that previously blocked P2-004 — the seed
> tag taxonomy and the automated DB-test execution policy — are now **resolved by
> `docs/decisions/DEC-0008-p2-seed-tags-and-db-test-policy.md`**. This document plus DEC-0008 are the
> active implementation contract. **P2-004 remains pending an explicit Nadav implementation
> authorization** — do not write the seed script or tests until it is issued. When authorized,
> implement **exactly** the DEC-0008 contract; the code agent must **not** re-decide any of it
> (`docs/coding-rules.md` §9).

## Closed decisions (see DEC-0008)

The decisions that previously left this task BLOCKED are now fixed; the code agent must **not**
re-decide them:

1. **UsageEvent uniqueness / idempotency key** — **resolved** as **`UNIQUE(song_id, event_type)`**
   (`DEC-0006` §8), already implemented and structurally tested in P2-002.
2. **The success/Ready state value** — **resolved**: a billable `separation_succeeded` row exists only
   when `SeparationJob.status = succeeded` **and** `Song.status = ready` (`DEC-0006` §3-enums, §8),
   already implemented.
3. **Default tag taxonomy** — **resolved** as a **labelled placeholder** set of exactly four tags
   (DEC-0008 §2). Not final product taxonomy; implies no public-library behavior.
4. **Automated DB-test execution policy** — **resolved**: SQLite in-memory built via
   `metadata.create_all()`; the suite stays runnable without live PostgreSQL (DEC-0008 §5, §6).

**Rule:** implement exactly the DEC-0008 contract. Do not invent tags, uniqueness keys, finalizer
logic or a test-DB policy, and do not add any dependency.

## Implementation notes (when later authorized)

- **Use exactly the four placeholder tags** from DEC-0008 §2 — `vocals`→Vocals, `background`→Background,
  `instrumental`→Instrumental, `demo`→Demo. **No other tag** may be seeded.
- **Create the seed script (`backend/scripts/seed_tags.py`) only if explicitly authorized** in the
  P2-004 implementation prompt. It must be idempotent by `slug`, run only on deliberate operator
  invocation (never on app or Docker Compose startup), not be an Alembic data migration, target local
  Compose Postgres only, and insert **only** the four tags (DEC-0008 §3, §4).
- **Automated tests use SQLite in-memory** (`metadata.create_all()`) for seed-idempotency and
  constraint checks (DEC-0008 §5, §7). The automated suite must remain runnable with **no** live
  database.
- **Live Compose Postgres / `alembic upgrade` is optional manual verification only** — never required
  for automated P2-004 acceptance, never a production DB (DEC-0008 §6).
- **No finalizer / business-logic tests.** Failed-processing is asserted **structurally only** in
  P2-004; **behavioral failed-processing tests are deferred to P5/P7** when finalization logic exists
  (DEC-0008 §8).
- **No API / upload / queue / Redis / storage / MinIO/S3 / AI / frontend / worker work**, no new or
  deferred entities, no schema changes, no production DB (DEC-0008 §9, §11).

## Required DB tests when implemented

The full, closed test contract is **DEC-0008 §10**; the code agent must satisfy it exactly. Live-engine
tests use **SQLite in-memory** built via `metadata.create_all()` (DEC-0008 §5) — the automated suite
stays runnable with **no** live PostgreSQL. In summary:

1. **Seed idempotency test** — running the seed twice against a fresh SQLite in-memory DB produces the
   same four tag rows, no duplicates, no error (DEC-0008 §4).
2. **UsageEvent uniqueness / idempotency test** — the key is approved (`UNIQUE(song_id, event_type)`,
   `DEC-0006` §8): prove the DB **rejects a duplicate success finalization** (a real constraint
   violation, not application-level checking). Evidence Phase 7 quota finalization depends on; guards
   `R-006`. Companion uniqueness checks for `Tag.slug`, `SongTag`, `DailyUsage` and
   `AudioFile (song_id, purpose)` per DEC-0008 §7.
3. **Failed-processing (structural only)** — assert `UsageEvent.event_type` allows only
   `separation_succeeded` and that no P2 code path creates usage for a `failed`/`canceled` job. **Do
   not** invent or exercise a finalizer; **behavioral failed-processing tests are deferred to P5/P7**
   (DEC-0008 §8).
4. **Deterministic constraint naming** — unique-constraint names follow the DEC-0005 convention
   (e.g. `uq_tags_slug`, `uq_usage_events_song_id`), not backend-generated names.
5. **Automated no-audio-bytes-in-DB / no-path / no-URL / storage_key-internal** guards — including the
   seed path; **no audio bytes in DB**, no `LargeBinary` / `BYTEA` audio columns (DEC-0008 §9).
6. **Existing P2-001/P2-002/P2-003 tests still pass; Phase 0/1 regression tests still pass.**

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

Do not start. The blocking decisions are now closed by
`docs/decisions/DEC-0008-p2-seed-tags-and-db-test-policy.md`, but P2-004 implementation begins only
after P2-002/P2-003 are accepted (they are) **and** an explicit Nadav authorization for P2-004 is
issued. When authorized, implement exactly the DEC-0008 contract (seed only the four placeholder tags;
SQLite in-memory automated tests; Compose Postgres/Alembic optional manual verification only;
structural failed-processing only), run the test contract above, return the evidence report, and stop;
do not continue to Phase 3.
