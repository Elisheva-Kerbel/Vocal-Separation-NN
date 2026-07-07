# P0-006 — README, Coding Rules and Phase 0 Closure

Status: **Implemented (P0-006 authorized) — pending readiness review of the evidence.**
Phase: 0 (Dockerized Project Skeleton) · Package: PKG-P0 · Source: `stemspace-dev-pack-v0.1/tasks/phase-0/TASK-P0-006-readme-and-coding-rules.md`

> This task **is** the currently authorized Phase 0 task. It finalizes the Phase 0 documentation
> (README, `docs/coding-rules.md`, scope boundaries) and **documents — but does not execute —**
> the Phase 0 final closure gate (see `phase-0-final-closure-gate.md`). It is documentation only:
> no application, Docker, frontend, backend or worker behaviour changes. Repo docs stay **Draft**
> until a readiness review PASSes; nothing here implies approval or authorizes a later phase.

## Goal

Document local development, coding rules and scope boundaries for Phase 0, and define the
**Phase 0 closure evidence** that proves the dockerized skeleton is ready.

## Scope

Write scope: `README.md`, `docs/coding-rules.md`, `docs/decisions/` (DEC-0001, DEC-0002 and,
for storage boundary, DEC-0003). No network access.

## What to build

- Documentation of the project purpose.
- Documentation of the local Docker Compose service overview.
- Documentation of the no-secrets policy.
- Documentation of the minimal-code rule.
- Documentation of what Phase 0 does **not** build.
- Documentation of the evidence expected from implementation tasks, including the Phase 0
  closure evidence checklist below.

## What NOT to build

- No unapproved production deployment documentation.
- No real credentials.
- No content that implies Nadav approval.
- **Phase 0 boundary (must be stated explicitly in the docs):** no upload API, no queue
  processing, no DB domain models, no auth, no AI model execution, no billing, no admin, no
  public library, no public storage, no resumable upload, no extra stems.

## Acceptance criteria

- The README is clear.
- Coding rules exist.
- Docs contain no secrets.
- Status remains **Draft** until Nadav returns a readiness PASS.
- The Phase 0 closure evidence checklist (below) is documented and required.

## Required checks / tests

- Markdown readability review.
- Confirmation that no execution authorization is implied and no secrets are present.

## Phase 0 closure evidence — REQUIRED

The **authoritative, full Phase 0 final closure gate** is documented in
`phase-0-final-closure-gate.md`. That gate is **documented, not executed** as part of P0-006; it
is run only when a separate review explicitly authorizes Phase 0 closure. The summary below
captures the core service-startup evidence (Phase 0 is closable only after **all** of it, plus
the full gate, is demonstrated):

1. `docker compose config` is valid.
2. `docker compose up --build` starts all local services.
3. Backend `/health` is reachable.
4. Frontend loads.
5. Worker starts.
6. **PostgreSQL** is reachable by the backend/worker via its **Compose service name**.
7. **Redis** is reachable by the backend/worker via its **Compose service name**.
8. **MinIO** is reachable by the backend/worker via its **Compose service name**.

Plus: no real secrets, and no business logic.

## Evidence expected

- Changed files.
- The full Phase 0 closure evidence above (command outputs / screenshots where relevant).
- Confirmation that status remains Draft and no false approval is claimed.
- Deviations, blockers and a confirmation that no out-of-scope work was done.

## Stop gate

Stop after this task. Run only the approved checks. Return changed files, checks, evidence,
deviations and blockers. **Do not continue past Phase 0 without review.**
