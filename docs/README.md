# Project Documentation

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**

This folder holds project documentation and task-level Markdown files for StemSpace. The original
source baseline is the development pack at `../stemspace-dev-pack-v0.1/`; the files here adapt that
pack into repo-local, actionable documentation.

## Source of truth and load order

- The Dev Pack under `../stemspace-dev-pack-v0.1/` is **read-only historical source**. **Do not edit
  the Dev Pack.**
- For **Phase 2 implementation**, the **active implementation contract** is the repo-local
  `docs/tasks/phase-2/*` together with `docs/decisions/DEC-0005-db-base-session-and-migration-determinism.md`
  (DB foundation) and `docs/decisions/DEC-0006-phase-2-domain-data-contract.md` (the P2-002 domain
  data contract: entity fields, states, uniqueness/idempotency keys and `storage_key` shape).
- **Where repo-local Phase 2 docs differ from the original Dev Pack task files, use the repo-local
  docs and DEC-0005.** They are newer and deliberately supersede the pack's Phase 2 task text — for
  example P2-001's write scope was widened (to include `backend/requirements.txt` and
  `backend/app/config.py`) and its test contract made explicit, because the pack's version was not
  executable as written.
- The Dev Pack remains authoritative for anything the repo-local docs do not supersede: project
  boundaries, `AGENT.md`, the phase/package structure, and the evidence template.

## Structure

- `tasks/phase-0/` — the six Phase 0 task documents (Goal, Scope, What to build, What not to
  build, Acceptance criteria, Required checks/tests, Evidence expected, Stop gate), plus
  `phase-0-final-closure-gate.md`, which documents (but does not execute) the Phase 0 closure gate.
- `tasks/phase-1/` — Phase 1 task documents (AI benchmark harness / Basic local prototype).
- `tasks/phase-2/` — Phase 2 readiness and task documents. `P2-000-readiness-fixes.md` records the
  readiness fixes; `P2-001-db-base-and-alembic.md` is prepared but **not authorized**; the
  `P2-002`/`P2-003`/`P2-004` docs are **guardrails only** and remain blocked on open decisions.
- `decisions/` — decision records (DEC-####) capturing implementation boundaries. `DEC-0005` fixes
  the DB base, sync SQLAlchemy session, config/DB-URL handling and Alembic migration determinism
  for Phase 2; `DEC-0006` fixes the Phase 2 domain data contract (per-entity fields, state/enum
  values, relationships, uniqueness/idempotency keys, indexes and the `storage_key` shape) so
  P2-002 can be implemented mechanically.
- `coding-rules.md` — stack conventions, minimal-code policy, security and Phase 0 boundaries.
- `git-workflow.md` — commit conventions (cadence, commit size, message style).
- `prd/` — PRD references, added when the PRD artifact is supplied.
- `architecture/` — architecture / low-level-design references, added when supplied.
- `spike/` — spike and evaluation results, such as AI benchmark evidence.

The `prd/`, `architecture/` and `spike/` folders currently contain only a `.gitkeep`
placeholder; they are populated when the corresponding content is approved and supplied.

## How to use these docs

- Work on **one approved task at a time**. Do not implement a later task's scope.
- Each task document is self-contained: it states exactly what to build, what not to build,
  how it is verified, and where it must stop.
- Every implementation task ends with an **evidence report** using
  `../stemspace-dev-pack-v0.1/templates/evidence-report-template.md`.

## Status labels

All docs here remain **Draft** until Nadav returns a readiness PASS on the exact pack version.
Nothing in this folder authorizes AI code agent execution beyond the currently approved task.
