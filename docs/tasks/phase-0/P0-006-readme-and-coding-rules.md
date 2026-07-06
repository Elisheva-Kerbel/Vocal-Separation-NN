# P0-006 — README, Coding Rules and Phase 0 Closure

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**
Phase: 0 (Dockerized Project Skeleton) · Package: PKG-P0 · Source: `stemspace-dev-pack-v0.1/tasks/phase-0/TASK-P0-006-readme-and-coding-rules.md`

> This task is **not** authorized yet. It is documented here for Phase 0 completeness. Do not
> implement it until it is the approved task.

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

Phase 0 is closable only after **all** of the following is demonstrated (this is a required
Stop Gate for Phase 0 closure, strengthened from the pack's phase acceptance criteria):

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
