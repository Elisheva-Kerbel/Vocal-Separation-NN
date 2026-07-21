# DEC-0008 — P2-004 seed taxonomy and DB test execution policy

Status: **Approved for P2-004 planning / pending Nadav implementation authorization.**
Not an implementation authorization. Not production-approved. No public users. No public-library behavior.

Phase: 2 (Backend Domain + DB Skeleton) · Package: PKG-P2 · Recorded by: DEC-0008 seed/DB-test-policy work
Relates to: `DEC-0002` (minimal code), `DEC-0003` (private storage only), `DEC-0004` (local model prototype),
`DEC-0005` (DB base / session / migration determinism), `DEC-0006` (Phase 2 domain data contract),
`DEC-0007` (P2-003 schema contract), `docs/coding-rules.md`,
`docs/tasks/phase-2/P2-004-seed-tags-and-db-tests.md`
Baseline (read-only historical): `stemspace-dev-pack-v0.1/tasks/phase-2/TASK-P2-004-seed-tags-and-db-tests.md`,
`stemspace-dev-pack-v0.1/packages/PKG-P2-backend-domain-db-skeleton.md`,
`stemspace-dev-pack-v0.1/phases/PHASE-02-backend-domain-db-skeleton.md`,
`stemspace-dev-pack-v0.1/06-security-permissions-and-secrets.md`,
`stemspace-dev-pack-v0.1/07-testing-and-evidence-strategy.md`, `stemspace-dev-pack-v0.1/09-risk-register.md`

> This record closes the two decisions that made the P2-004 readiness gate report **BLOCKED**: the
> **seed tag taxonomy** and the **automated DB-test execution policy** (the substrate for the required
> seed-idempotency and real-constraint-violation tests). It defines the **positive** contract so P2-004
> can later be implemented **mechanically**, without the code agent inventing product taxonomy or a
> live-DB test policy (`docs/coding-rules.md` §9). It authorizes **no** code, **no** seed script, **no**
> seed data, **no** database connection, **no** Alembic upgrade and **no** migration. P2-004
> implementation begins only after Nadav reviews this record and issues an explicit authorization
> (see §12).

## 1. Decision

Fix the two open P2-004 decisions on top of the DB foundation (`DEC-0005`) and domain data contract
(`DEC-0006`):

1. **Seed taxonomy** — P2-004 seeds a **minimal placeholder** tag set only (§2). It is **not** final
   product taxonomy and implies **no** public-library behavior.
2. **Automated DB-test execution policy** — P2-004 automated tests use **SQLite in-memory** built from
   the shared `Base.metadata` via `metadata.create_all()` (§5). The suite stays runnable **without**
   live PostgreSQL; a real Alembic upgrade against local Compose Postgres is **optional manual
   verification only** (§6).

This adds **no** new entity, **no** schema change, **no** dependency, **no** route, and **no**
finalizer/business logic. The `Tag` / `SongTag` tables and every uniqueness key already exist from
P2-002 (`DEC-0006` §4.5, §4.6, §8, §10); this record decides only *what to seed* and *how tests run*.

## 2. Approved placeholder tag taxonomy (exact, closed)

P2-004 may seed **exactly** these four tags — **no more, no fewer**. Each is a neutral placeholder that
carries **no** product-taxonomy claim and no public-library semantics.

| `slug` | `name` |
|---|---|
| `vocals` | Vocals |
| `background` | Background |
| `instrumental` | Instrumental |
| `demo` | Demo |

- **No other tag may be seeded in P2-004.** Adding, renaming or removing a seeded tag is a **future
  decision**, not a P2-004 action.
- These are placeholders to exercise the seed/idempotency path; the final product tag taxonomy (and any
  library/public surface that consumes it) is deferred to its approved phase (`DEC-0002`, `R-009`).
- `slug` is the stable machine key (matches `Tag.slug`, `uq_tags_slug`); `name` is the display label
  (`DEC-0006` §4.5). No other `Tag` field is set by the seed (`id` is application-assigned `uuid4`;
  `created_at`/`updated_at` are set by the model defaults).

## 3. Seed mechanism

P2-004 may create **one** file for seeding:

- `backend/scripts/seed_tags.py`

The seed script **must**:

- insert **only** the four approved placeholder tags (§2);
- be **idempotent by `slug`** (§4);
- **not** run automatically — it is invoked deliberately by an operator, never on import;
- **not** be called by application startup (`app/main.py`), the worker, or any Docker Compose
  service/command;
- **not** be an Alembic data migration (it is a standalone operator script, consistent with
  `DEC-0005` §11 "no auto-running migrations at app or container startup");
- **not** require or target a production database — **local Compose Postgres only** (`DEC-0005` §3, §9);
- **not** insert any product/user/song/job/usage data — tags only.

Reuse the existing `app.config` / `app.db` session wiring (`DEC-0005` §4, §7): the DB URL is read
through `config.py`, never via a scattered `os.getenv`, and is a repr-hidden secret. The script must
never log or echo `DATABASE_URL`, a password, or any secret.

## 4. Idempotency policy

- The seed is **idempotent keyed on `Tag.slug`** (`uq_tags_slug`): running it once creates the four
  tags; running it again produces the **same rows** — **no duplicates, no error**.
- Idempotency is achieved by an **insert-if-absent** strategy (look up by `slug`, insert only when
  missing). It must **not** depend on catching a raw `IntegrityError` as normal control flow, and must
  **not** mutate an existing tag's `name` in a way that would rewrite operator/product state
  unexpectedly (a placeholder re-seed is a no-op for already-present slugs).
- Idempotency is **proven by an automated test** (§5, §10): running the seed twice against a fresh
  SQLite in-memory database yields exactly the four tag rows both times.

## 5. Automated DB test substrate — SQLite in-memory + `metadata.create_all()`

- P2-004 automated tests that need a **live engine** (seed idempotency, real uniqueness-violation
  checks) use an **in-memory SQLite** engine whose schema is built from the shared `Base.metadata`
  via `metadata.create_all(engine)`. No migration run is required to build the test schema.
- This live-engine substrate is permitted **only** for **seed / idempotency / constraint** tests. All
  other P2-004 tests remain **metadata / migration-file inspection** in the existing repo style
  ("no engine, no connection").
- **Compose Postgres is not required** for any automated P2-004 test. The suite must stay runnable on
  a developer machine or CI with **no database service up**, preserving the `DEC-0005` §4/§10 property
  that importing `app.db` opens no connection and the automated contract needs no live DB.
- Test engines are created **inside the test** (fixture-scoped) and disposed at teardown; nothing
  connects at import time.

## 6. Live PostgreSQL / Alembic policy

- The P2-004 **automated** test suite **must remain runnable without live PostgreSQL**.
- Running `alembic upgrade` against **local Compose Postgres** is **optional manual verification
  only** — it is **not** required for automated P2-004 acceptance (this restates `DEC-0005` §10:
  a migration actually run against local Compose Postgres is manual verification, permitted only when
  explicitly authorized).
- **No production DB.** No production host, credential, or non-local connection target — in the seed
  script, in tests, or in committed configuration (`DEC-0005` §7, §9).
- If the manual Postgres path is exercised, it uses a **local/test `DATABASE_URL`** via `config.py`,
  writes **only** the approved seed tags (if seeding is exercised), never echoes `DATABASE_URL`, and
  is torn down after verification.

## 7. Real constraint-violation tests (SQLite where compatible)

Using the §5 SQLite substrate, P2-004 may prove that the **database rejects a duplicate** for the
already-defined uniqueness keys (a real constraint violation, not application-level checking):

- `Tag.slug` uniqueness (`uq_tags_slug`);
- `SongTag` composite-PK uniqueness (`pk_song_tags` on `(song_id, tag_id)`);
- `UsageEvent` uniqueness (`uq_usage_events_song_id` on `(song_id, event_type)`) — the `R-006`
  double-count guard;
- `DailyUsage` uniqueness (`uq_daily_usage_user_id` on `(user_id, usage_date)`);
- `AudioFile` uniqueness (`uq_audio_files_song_id` on `(song_id, purpose)`).

SQLite enforces `UNIQUE`, composite `PRIMARY KEY` and `CHECK` constraints, so these are faithfully
testable there. **Limitation clause:** if any specific constraint cannot be faithfully exercised in
SQLite (e.g. a semantic that depends on PostgreSQL-specific behavior, or SQLite foreign-key
enforcement being off by default), the test **reports that as a documented limitation** and falls back
to the existing **metadata / migration-file** assertion for that constraint — it does **not** invent a
Postgres requirement into the automated suite.

## 8. Failed-processing test policy

- P2-004 must **not** invent finalizer or business logic, and **no** P2-004 test may require a
  non-existent finalization/quota service. The finalize/rollup logic is explicitly P5/P7
  (`DEC-0006` §8).
- For P2-004, "failed processing creates no billable usage" (`R-005`) is asserted **structurally
  only**:
  - `UsageEvent.event_type` allows **only** `separation_succeeded` (the single billable/final event —
    `DEC-0006` §3-enums, §4.7);
  - the `UsageEvent` uniqueness key applies to **successful finalization** only (`(song_id,
    event_type)`), so at most one billable finalization per song;
  - **no application code exists** in Phase 2 that creates a usage row for a `failed`/`canceled` job
    (there is no finalizer to exercise).
- **Behavioral** failed-processing tests (asserting a running finalizer skips non-success jobs) are
  **deferred to P5/P7**, when the finalization logic actually exists.

## 9. Security / data-safety tests (binding; restated for seeds)

P2-004 must verify or preserve, extended to cover the seed path (`DEC-0005` §9, `DEC-0006` §5–§7):

- **no audio bytes in DB** — the seed inserts no binary audio; no `LargeBinary` / `BYTEA` audio column;
- **no checkpoint/model/local filesystem path columns** — and no seed/default/fixture writes a
  checkpoint path, model path, operator-machine path or `LOCAL_MODEL_ROOT` value;
- **no signed-URL string columns** — and no seed/fixture persists one;
- **no public-URL columns** — no public bucket/object/permanent URL;
- **`storage_key` remains internal** — present only on `AudioFile`, never in a client/API schema
  (P2-003), and never printed into committed seed/test output;
- **`DATABASE_URL` never logged or echoed** — not by the seed, not in test output, not in a
  connection-failure message;
- **no API / upload / queue / Redis / storage / MinIO/S3 / AI integration** is introduced;
- **no frontend or worker behavior change**.

## 10. P2-004 test contract (required when implemented)

All must pass; the automated suite runs with **no live PostgreSQL** (§5, §6):

1. **Seed idempotency** — running the seed twice against a fresh SQLite in-memory DB yields exactly the
   four approved tag rows both times; no duplicates, no error (§4).
2. **Seed content is exactly the four placeholder tags** — the seed creates the §2 `slug`/`name` set
   and nothing else.
3. **Real uniqueness-violation** — the DB rejects a duplicate for each §7 key that is SQLite-testable;
   otherwise the documented-limitation fallback applies.
4. **Deterministic constraint naming** — the relevant unique constraints carry DEC-0005-convention
   names (e.g. `uq_tags_slug`, `uq_usage_events_song_id`), not backend-generated names.
5. **Failed-processing (structural)** — `UsageEvent.event_type` allows only `separation_succeeded`;
   no code path creates usage for a `failed`/`canceled` job (§8).
6. **No-audio-bytes / no-path / no-URL / storage_key-internal** guards hold, including the seed path
   (§9).
7. **Existing P2-001 / P2-002 / P2-003 tests still pass** — DB scaffold, model, constraint, migration
   and schema no-leak suites are unaffected.
8. **Phase 0/1 regressions still pass** — `/health`, config, worker startup and the AI-boundary
   lazy-import test are unaffected.

`07-testing-and-evidence-strategy.md` treats seed idempotency and UsageEvent-uniqueness evidence as
Phase 2 evidence; these tests are that proof, and PKG-P2 makes the UsageEvent-uniqueness evidence the
contract Phase 7 quota finalization depends on.

## 11. Scope / out of scope

**P2-004 may implement:** `backend/scripts/seed_tags.py` (§3); seed tag tests; DB constraint /
idempotency tests (§5, §7); migration / metadata-parity tests if needed; regression checks.

**P2-004 must NOT implement:** new domain entities; deferred entities; changes to existing entity
fields; schema changes; API routes; upload flow; queue processing; Redis; MinIO/S3; storage client;
signed-URL generation; AI integration; frontend; worker processing; production DB / production
migrations; public-library behavior; finalizer/quota business logic. No dependency is added by P2-004.

## 12. Source-of-truth note & authorization boundary

- **DEC-0008 and the repo-local `docs/tasks/phase-2/P2-004-seed-tags-and-db-tests.md` are the active
  implementation contract for P2-004.** Where the read-only Dev Pack (`stemspace-dev-pack-v0.1/*`)
  differs, these repo-local docs win; the Dev Pack remains authoritative for anything they do not
  supersede (project boundaries, `AGENT.md`, the evidence template).
- **Authorization boundary:** DEC-0008 closes the *decisions*; it authorizes **no** code, seed script,
  seed data, dependency, database connection, Alembic upgrade or migration. P2-004 implementation
  begins only after **Nadav** reviews this record and issues an explicit implementation authorization.
  **Phase 3 onward remain out of scope** and unauthorized.

## Rationale

The P2-004 readiness gate reported BLOCKED because two things were undefined: the seed tag taxonomy
(none supplied) and the execution substrate for the required seed-idempotency and real-constraint
tests (the repo's DB tests were all metadata-only, and `DEC-0005` §10 treats live-Postgres runs as
authorized-only manual verification). Left open, the code agent would have had to invent product
taxonomy and a test-DB policy — exactly what `docs/coding-rules.md` §9 forbids. Fixing a labelled
placeholder set and an in-memory SQLite substrate here, in an authority-owned record, converts P2-004
into a mechanical, testable task that keeps the suite DB-free while still proving the `R-005`/`R-006`
uniqueness evidence Phase 7 depends on — without pulling any deferred product, storage or finalizer
behavior forward.
