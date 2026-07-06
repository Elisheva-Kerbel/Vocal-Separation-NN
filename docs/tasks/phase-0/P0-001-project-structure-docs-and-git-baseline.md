# P0-001 — Project Structure, docs/ Task Files and Git Baseline

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**
Phase: 0 (Dockerized Project Skeleton) · Package: PKG-P0 · Source: `stemspace-dev-pack-v0.1/tasks/phase-0/TASK-P0-001-project-structure-docs-and-git-baseline.md`

## Goal

Create the minimal monorepo folder structure, the documentation folder and the Git baseline
files, so Phase 0 has a clean foundation and clear task-level docs inside the repo.

## Scope

- Repository skeleton folders and `.gitkeep` placeholders.
- `docs/` structure with a README, coding rules, git workflow, decision records and the six
  Phase 0 task documents.
- Git baseline files: `.gitignore`, `.gitattributes`, `.editorconfig`, plus root `README.md`
  and `.env.example` (placeholders only).
- Write access is limited to skeleton, docs and Git baseline files only.

## What to build

- The approved top-level layout: `backend/`, `frontend/`, `infra/`, `docs/`.
- `docs/README.md` describing the docs structure.
- `docs/coding-rules.md` and `docs/git-workflow.md`.
- `docs/tasks/phase-0/` with the six Phase 0 task documents (this file and P0-002…P0-006).
- `docs/decisions/DEC-0001-compose-first-local-dev.md`,
  `DEC-0002-minimal-code-no-overengineering.md`, `DEC-0003-private-storage-only.md`.
- `docs/prd/`, `docs/architecture/`, `docs/spike/` as `.gitkeep` placeholders (approved docs
  structure; populated later when content is supplied).
- `.gitignore`, `.gitattributes`, `.editorconfig`, root `README.md`, `.env.example`.
- `.gitkeep` only where an otherwise-empty directory must be retained.

## What NOT to build

- No product/application code (backend, frontend or worker).
- No `docker-compose.yml`, no Dockerfiles, no `.dockerignore` (those are P0-002).
- No dependency installation, no app generators.
- No CI/CD workflows.
- No auth, upload, AI, DB domain models, API routes or queue behavior.
- **Phase 0 boundary:** no upload API, no queue processing, no DB domain models, no auth, no AI
  model execution, no billing, no admin, no public library, no public storage, no resumable
  upload, no extra stems.

## Acceptance criteria

- The required folder tree exists.
- The required docs task files exist and are **useful, non-stub** documents.
- The three decision records exist.
- Git baseline files exist (`.gitignore`, `.gitattributes`, `.editorconfig`) and `.gitignore`
  excludes `.env`/local env files, Python caches, virtualenvs, `node_modules`, frontend build
  outputs, logs, `local-data`, OS/editor noise and test/cache artifacts, while **not** ignoring
  `.env.example`.
- No business logic files were added.
- No secrets or real credentials (only placeholders).

## Required checks / tests

- File-existence / tree inspection of the created structure (no automated product tests are
  required for this task).
- Grep confirming the six task docs are not stubs and contain the required sections.
- Grep confirming no real secrets are present (only placeholders such as `change_me_local_only`).
- If Git is initialized: `git status --short`.

## Evidence expected

- List of changed/created files.
- Folder tree output.
- Result of the existence/stub/secret checks.
- Manual verification (docs open and are readable; Git baseline files are readable).
- Deviations, blockers and a confirmation that no out-of-scope work was done.

## Stop gate

Stop after this task. Run only the approved checks. Return changed files, checks, evidence,
deviations and blockers. **Do not continue to P0-002.**
