# DEC-0009 — Local demo vertical slice

Status: **Approved for local demo planning / pending Nadav implementation authorization.**
Not an implementation authorization. Not production-approved. Not commercially approved. No public users.
Professional is **not** implemented and must not be presented as implemented.

Phase: FAST-DEMO (a deliberately scoped local-demo track alongside the numbered phases) · Package: none
Recorded by: FAST-DEMO-001 readiness review + FAST-DEMO-002 in-container inference proof
Relates to: `DEC-0002` (minimal code), `DEC-0003` (private storage only), `DEC-0004` (Basic local model
prototype), `DEC-0006` (domain data contract), `DEC-0007` (schema contract), `docs/coding-rules.md`,
`docs/tasks/phase-1/P1-004C-real-audio-validation.md`
Baseline (read-only historical): `stemspace-dev-pack-v0.1/02-product-scope-and-do-not-build.md`,
`stemspace-dev-pack-v0.1/04-minimal-code-policy.md`, `stemspace-dev-pack-v0.1/05-architecture-and-stack.md`,
`stemspace-dev-pack-v0.1/06-security-permissions-and-secrets.md`

> This record exists because the local demo **cannot** be built under the current rules without an
> authority-owned exception: three approved boundaries explicitly forbid parts of it (§3). `docs/coding-rules.md`
> §9 forbids the code agent from deciding this for itself, so the exception is recorded here instead.
> DEC-0009 authorizes **no** code. It fixes *what may be built* and *what must not*, so FAST-DEMO-003/004/005
> can later be implemented mechanically. Implementation begins only after Nadav issues an explicit
> per-task authorization (§12).

## 1. Decision

Authorize a **local-only demo vertical slice**: a single, minimal path from a browser upload to a
Vocals + Background result produced by the **Basic local model**, running entirely on the operator's
machine. The slice is granted a **tightly scoped, enumerated set of deviations** (§3) from boundaries
that remain fully in force everywhere else.

The demo track is **additive and temporary**. It changes **no** phase contract: Phase 3 (auth), Phase 4
(upload + private storage), Phase 5 (queue/worker), Phase 6 (result page + signed URLs) still own the
real implementation and are unaffected by anything decided here. Nothing in the demo may be cited later
as precedent, as an implemented feature, or as production readiness.

## 2. Purpose

Show a working StemSpace demo quickly, locally:

**Frontend upload → backend processing → Basic local model → Vocals + Background result screen.**

The audience is internal review. The goal is to make the existing, already-proven separation capability
visible end to end — not to build product surface early.

## 3. Explicit deviations — approved for the local demo only

Each deviation names the rule it departs from. Every rule stays binding outside the demo slice.

| # | Deviation | Departs from | Confinement |
|---|---|---|---|
| **D1** | AI inference may run **inside one local HTTP request** (synchronous). | `coding-rules.md` §2 — *"No AI inference inside the HTTP request path."* | Local demo process only. The real flow stays async (Phase 5). |
| **D2** | Demo **API routes** may be added, under the `/demo` prefix **only**. | `DEC-0004` §6 — *"No upload / queue / DB / API / Redis / MinIO-S3 / frontend / worker integration."* | Only the two routes in §5. No other route, prefix or router. |
| **D3** | A **frontend upload/result screen** may be added. | `DEC-0004` §6 (frontend integration); Phase 0 *"no product UI"*. | Exactly the one page in §6. |
| **D4** | **Local disk** temp storage may be used for demo inputs/outputs. | `coding-rules.md` §3 — *"Local dev storage is MinIO / a local adapter."* | Private, backend-mediated, ephemeral (§7). The **private-only** rule itself is **not** waived. |
| **D5** | **MinIO / S3 is not required** for the demo. | `DEC-0003` phase relevance; `coding-rules.md` §3. | The storage client and signed URLs remain Phase 4/6 work, unstarted. |
| **D6** | **DB writes are not required** for the demo. | Phase 2 domain model exists but is not exercised. | Demo job state is in-process only. No table is read or written (§4). |
| **D7** | **Queue / worker is not required** for the demo. | `coding-rules.md` §4 (Redis + Celery, one queue). | The worker stays the Phase 0 startup stub, unchanged. |
| **D8** | **Plain React + CSS is preferred** over adding a UI library. | `coding-rules.md` §2 — *"Mantine UI preferred."* | No new npm dependency (§6). Reason: a dependency change forces an in-container `npm install`, which is a known failure mode behind a TLS-intercepting proxy. |

**No other deviation is approved.** Anything not listed above remains governed by the existing rules; if
the implementation appears to need a further exception, that is a **blocker to raise**, not a decision
for the code agent to make.

## 4. Hard boundaries (binding)

The demo slice must be:

- **local demo only** — one operator, one machine;
- **Basic model only** — `use_best_model` stays a server-side internal selector (`DEC-0004` §5);
- **no Professional** — not implemented, not selectable, not referenced in UI or API as if it existed;
- **no production claim**, **no commercial claim**, **no public users**.

The demo slice must **not** introduce:

- auth / login / sessions / users;
- billing, quotas, coupons;
- admin, RBAC, audit;
- public library, My Library, ratings, sharing;
- queue, Celery, Redis, worker processing;
- MinIO / S3 / any storage client or bucket;
- signed URLs (nothing to sign — no object storage is used);
- **DB writes** (or reads) — no session, no model use, no migration run;
- committed model / checkpoint / audio files (`DEC-0004` §4 — permanent rule);
- **local host paths** anywhere in the repository (committed files, tests, fixtures or docs);
- `storage_key` in any response — the field stays internal to `AudioFile` (`DEC-0006` §5, `DEC-0007` §7);
- a checkpoint path, filename, internal reference or `LOCAL_MODEL_ROOT` value in any response, log,
  error message, metric or UI string (`DEC-0004` §9, P1-002);
- any secret or path leakage in output of any kind.

## 5. Demo backend contract

**Exactly two routes**, both under `/demo`:

**`POST /demo/separate`**
- Accepts one audio payload (§8) and runs the separation **synchronously** (D1), server-side, using the
  existing `ai.local_inference` adapter unchanged.
- The model tier is fixed **server-side to Basic**. The client sends **no** tier, **no** checkpoint
  reference and **no** path — as with the benchmark CLI, only an internal boolean selector exists.
- Success response is JSON carrying an opaque `jobId`, a status, and exactly **two** stem entries
  (`vocals`, `background`), each with a **backend route URL** — never a storage key, filesystem path or
  public URL.
- Failure returns a safe HTTP status with a **fixed coded reason** in the existing
  `scripts/run_benchmark.py` style (e.g. `local_model_not_configured`, `local_checkpoint_unavailable`,
  `local_dependency_missing`, `input_too_large`, `unsupported_input`). No traceback, no path, no echo of
  attacker-supplied input.

**`GET /demo/jobs/{jobId}/stems/{stem}`**
- `jobId` must be an **opaque UUID**, validated as a UUID before use.
- `stem` is limited to **`vocals` | `background`** (the existing `ai.model.Stem` values). No third stem
  may exist or be requestable.
- Returns the file through a **backend-mediated file response** only.
- The on-disk path is composed **server-side** from the validated `jobId` and `stem`. **No path-derived
  client input**: no client-supplied string may ever become a path segment, and no traversal input can
  reach the filesystem.
- Unknown `jobId` / invalid `stem` → 404 with a safe body.

Additionally binding:

- **No static directory exposure** — no `StaticFiles` mount, no directory listing, no route that serves
  an arbitrary path.
- **No public URL** and no permanent URL (`DEC-0003` stays in force).
- **No status/polling route** — processing is synchronous, so none is needed. Do not add one.
- **Sync processing is allowed** (D1); declare the route so the event loop is not blocked (a plain
  `def` route runs in the threadpool).
- **Placement:** keep the demo in a **flat module** under `backend/app/`. Do **not** create
  `app/api/`, `app/routers/` or `app/services/` — their absence is asserted by an existing P2-003 test.
- **Schemas:** define any demo response model **inside the demo module**. Do **not** add classes to
  `app/schemas/` — its class set is closed by `DEC-0007` and asserted by an existing test.
- **Existing boundary test:** `backend/tests/test_health.py::test_no_out_of_scope_routes` currently
  asserts that product routes do not exist. It must be **deliberately re-scoped** in FAST-DEMO-003 to
  allow `/demo/*` while still forbidding `/auth`, `/login`, `/songs`, `/library`, `/admin`. It must not
  be deleted or weakened beyond that.
- **`GET /health` is unchanged.** No other backend behavior changes.

## 6. Demo frontend contract

**One clean page**, three states, nothing more:

- **Upload / select file** — a single file input, visible constraints (accepted formats, size cap,
  expected wait).
- A **"Basic · local demo"** label, so no viewer can mistake the demo for a product tier or production.
- **Processing state** — an indeterminate indicator plus honest copy (e.g. "this usually takes under a
  minute"). **No fake progress**: no invented percentage, no simulated ETA.
- **Result state** — exactly **two** audio players (Vocals, Background) with **download links**, plus a
  reset to run another file.
- **Error state** — one inline, safe message; the page stays usable.

Must **not** contain: login/auth UI, library or history, admin, payment/billing/quota UI, a
**Professional selector** or any tier chooser, sharing, ratings, or navigation to non-existent pages.

Implementation constraints: **plain React + CSS** (D8); **no new npm dependency**; API calls go through
a small `frontend/src/api` module per `coding-rules.md` §2; no business logic in components; no messy
inline CSS. Clean and intentional, but not overbuilt.

## 7. Storage contract

- **Local temp folder only**, server-side, inside the backend container.
- **`DEMO_DATA_DIR`** (already present as a placeholder in `.env.example`) **may** be used as the root.
- Each job gets its own subdirectory keyed by the **opaque `jobId`**.
- Demo artifacts are **ephemeral** — they live only for the container's lifetime and carry no guarantee
  of persistence.
- **No committed outputs.** No audio file, input or output, may enter Git (`DEC-0004` §4). The existing
  `.gitignore` entries (`local-data/`, `backend/outputs/`, `backend/tmp/`, `*.wav`, `*.mp3`) already
  cover this and must not be relaxed.
- **No public file serving** — access only via the §5 route.
- **Cleanup policy may be minimal**: deleting the previous job's directory when a new job starts (or an
  equivalent trivial policy) is sufficient. No scheduler, no retention service, no background sweeper.

## 8. Input constraints

- **Byte cap is required.** Default **20 MB**, enforced **before** the payload is buffered or written.
  Over-cap input is rejected with a safe coded reason. (Rationale: the FAST-DEMO-002 fixture was ~8.4 MB;
  20 MB leaves headroom without inviting unbounded memory use.) The operator may lower it.
- **MP3 and WAV are both allowed.** FAST-DEMO-002 established that the current image decodes MP3 through
  the bundled libsndfile with **no ffmpeg present**, so MP3 is a supported demo input rather than
  best-effort. **Do not add ffmpeg** to the image for the demo.
- **No hard duration cap is required.** FAST-DEMO-002 separated a **3 min 40 s** track in **~35 s** with
  no memory failure, which supersedes the precautionary duration cap proposed in FAST-DEMO-001. Inputs
  materially longer than ~4 minutes are **unproven**; if one fails, fail safely rather than adding a cap
  by improvisation.
- **No new dependency for multipart** unless separately approved. `python-multipart` is **confirmed
  absent** from the backend image, and adding it invalidates the cached pip layer — forcing a full
  reinstall including torch, a known failure mode behind a TLS-intercepting proxy.
  **Prefer accepting the raw request body** (filename / content type via header or query parameter),
  which needs no new dependency and no image rebuild.
- Rejected input must never be echoed back into an error message.

## 9. Testing contract

Required when FAST-DEMO-003/004 are implemented:

1. **Backend happy path with mocked inference** — the separation adapter is **mocked**; no test may
   require torch, a checkpoint, real audio or the `/models` mount. Asserts a `jobId` and exactly the two
   stems.
2. **Backend safe failure** — missing model configuration and missing checkpoint each produce a safe
   coded reason, no traceback and no path.
3. **Invalid stem / unknown job** — 404 with a safe body; a traversal-style `jobId` or `stem` never
   reaches the filesystem.
4. **No path / secret leak** — no response or error body contains a host path, `/models`, a checkpoint
   filename, `LOCAL_MODEL_ROOT`, a drive letter or any credential.
5. **No `storage_key` leak** — the field appears in no demo response (it is not even used by the demo).
6. **Frontend build** — `npm run build` passes with no new dependency.
7. **E2E manual run evidence** — FAST-DEMO-005; evidence stays **out-of-band**, with no path, no audio
   and no metric values committed (`DEC-0004` §4, P1-004C precedent).
8. **Existing Phase 0/1/2 regressions still pass** — `/health`, config, worker startup, the AI-boundary
   lazy-import test, and the full DB/schema suites, unchanged.

## 10. Sequence

| Task | Scope | State |
|---|---|---|
| **FAST-DEMO-003** | Backend demo slice (§5, §7, §8) + tests (§9.1–§9.5) | Planned, **not authorized** |
| **FAST-DEMO-004** | Frontend demo UI (§6) + build check (§9.6) | Planned, **not authorized** |
| **FAST-DEMO-005** | End-to-end local run + evidence (§9.7, §9.8) | Planned, **not authorized** |

Each requires its **own** explicit Nadav prompt. They are executed **one at a time**, in order, with an
evidence report and a stop gate between them (`docs/coding-rules.md` §9).

Already complete and not repeated here: **FAST-DEMO-001** (readiness review) and **FAST-DEMO-002**
(read-only `/models` mount + in-container Basic inference proof — accepted).

## 11. Out of scope

**Anything not required for the local demo vertical slice.** Explicitly including: auth; real upload
pipeline; private object storage and the storage adapter; signed URLs; queue/worker processing; DB
persistence of demo runs; billing/quotas/coupons; admin/RBAC/audit; public or personal library; ratings;
sharing; Professional tier; extra stems beyond Vocals + Background; production deployment,
configuration or hardening; CI; performance tuning; refactoring of `backend/ai/*`, the benchmark CLI,
the worker, the DB models, the schemas or the migrations.

The demo does **not** advance any numbered phase. Phase 3 onward remain unauthorized.

## 12. Authorization boundary

- **DEC-0009 and the repo-local `docs/tasks/fast-demo/*` documents are the active contract for the demo
  track.** Where the read-only Dev Pack differs, these repo-local docs win for the demo slice only; the
  Dev Pack remains authoritative for everything they do not supersede (project boundaries, `AGENT.md`,
  the evidence template).
- **DEC-0009 authorizes no code.** No route, no UI, no storage handling, no dependency, no image change
  and no commit follow from this record alone. Each FAST-DEMO task begins only after Nadav reviews this
  record and issues an explicit implementation authorization for that task.
- The §3 deviations are **granted to the demo slice only** and expire with it. They do not amend
  `coding-rules.md`, `DEC-0003` or `DEC-0004`, and they may not be reused to justify future work.

## Runtime facts established by FAST-DEMO-002 (informative)

Recorded so the FAST-DEMO-003 implementer does not have to re-derive or guess them:

- The local Basic model runs **inside the backend container** via a **read-only** mount at `/models`
  (`LOCAL_MODEL_ROOT=/models`); the model root itself stays out-of-band and out of Git.
- A **3 min 40 s** MP3 separated in **~35 s** of inference (~38 s wall clock), producing both stems and a
  path-free `metrics.json` with `success=true`, `modelTier=Basic`. No memory failure.
- **MP3 decodes without ffmpeg**; torch 2.13, librosa, soundfile and numpy are present in the image; the
  pip layer is **cached**, so no dependency change should be introduced casually.
- **`python-multipart` is absent** (§8).
- The full backend suite (**257 passed, 1 skipped**), the worker startup check and the frontend build all
  pass with the mount in place.

## Rationale

FAST-DEMO-001 found the demo technically shallow but procedurally blocked: the hard work (a validated
Basic separation adapter with server-side checkpoint resolution and no path leakage) already exists, yet
three approved boundaries forbid exactly the four things a demo needs — inference in a request, an API
route, a frontend screen, and somewhere to put the files. Leaving that unresolved would have forced the
code agent to either stall or quietly overrule an approved decision, which `coding-rules.md` §9 forbids.

Recording the exception here — enumerated, confined to a `/demo` prefix and a single page, and explicitly
non-precedential — buys the visible demo without spending Phase 4/5/6 design capital or weakening the
guarantees that actually matter: private-only access, no `storage_key` or checkpoint path in responses,
no weights or audio in Git, and no claim that Professional or production exists.
