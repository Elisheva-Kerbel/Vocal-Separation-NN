# P0-005 — Frontend Empty Shell

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**
Phase: 0 (Dockerized Project Skeleton) · Package: PKG-P0 · Source: `stemspace-dev-pack-v0.1/tasks/phase-0/TASK-P0-005-frontend-empty-shell.md`

> This task is **not** authorized yet. It is documented here for Phase 0 completeness. Do not
> implement it until it is the approved task.

## Goal

Create a minimal React + Vite frontend shell with the approved folder structure. The frontend
loads but builds no real pages beyond a skeleton.

## Scope

Write scope: `frontend/package.json`, `frontend/src/` skeleton. No external API calls except a
later, explicitly scoped backend health check.

## What to build

- A Vite React app shell.
- The approved `src/` folders (including an `src/api/` folder prepared for future calls, plus
  `components/`, `features/`, `hooks/`, `styles/`, `theme/`, `utils/` as needed).
- An empty/placeholder `App` with no business logic.

## What NOT to build

- No upload / result / public / admin pages.
- No business logic inside JSX.
- No duplicated API logic.
- No messy inline CSS.
- **Phase 0 boundary:** no upload API, no queue processing, no DB domain models, no auth, no AI
  model execution, no billing, no admin, no public library, no public storage, no resumable
  upload, no extra stems.

## Acceptance criteria

- The frontend loads.
- The approved folder structure exists.
- No real feature pages exist.
- No messy inline CSS.

## Required checks / tests

- **Frontend build/start smoke check is REQUIRED** — the frontend must build and/or start
  cleanly. *(Strengthened from the source's "if approved": this smoke check is a required
  Phase 0 readiness Stop-Gate check.)*
- Manual verification that the shell opens and shows no out-of-scope features.

## Evidence expected

- Changed files.
- Frontend build/start smoke check result (passing) and evidence the shell loads.
- Deviations, blockers and a confirmation that no out-of-scope work was done.

## Stop gate

Stop after this task. Run only the approved checks. Return changed files, checks, evidence,
deviations and blockers. **Do not continue to P0-006.**
