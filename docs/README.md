# Project Documentation

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**

This folder holds project documentation and task-level Markdown files for StemSpace. The
source of truth is the approved development pack at `../stemspace-dev-pack-v0.1/`; the files
here adapt that pack into repo-local, actionable documentation.

## Structure

- `tasks/phase-0/` — the six Phase 0 task documents (Goal, Scope, What to build, What not to
  build, Acceptance criteria, Required checks/tests, Evidence expected, Stop gate), plus
  `phase-0-final-closure-gate.md`, which documents (but does not execute) the Phase 0 closure gate.
- `decisions/` — decision records (DEC-####) capturing implementation boundaries.
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
