# Git Workflow — Saving and Committing Changes

Status: **Draft — pending Nadav readiness review.**

This document defines how work is saved into Git for StemSpace. The goal is a clean, readable
history where every commit is a meaningful, self-contained step — **not too large, not too
small** — with a **clear, appropriately sized message**.

## When to commit

Commit when you reach a coherent, working checkpoint, typically:

- after completing a feature or an approved task;
- after a meaningful, self-contained piece of progress within a larger task;
- before switching context, so work is not lost.

Do **not** wait until the end of a big task and dump everything into one giant commit, and do
**not** commit half-finished, broken states just to commit often.

## Commit size — the right granularity

- **One logical change per commit.** A commit should tell a single, understandable story.
- Prefer commits a reviewer can read in a minute. If a commit touches many unrelated concerns,
  split it. If a commit is a trivial fragment of a larger idea, fold it in.
- Keep documentation, configuration and code changes that belong together in the same commit;
  separate genuinely unrelated changes.
- Do not mix refactoring with behavior changes in the same commit when it can be avoided.

## Commit messages — the right length

Use an imperative subject line plus an optional short body:

```text
<imperative subject, ~50 chars, no trailing period>

<optional body: 1–5 short lines explaining what changed and why.
Wrap around 72 chars. Skip the body for trivial, self-explanatory changes.>
```

- Subject: concise but descriptive — e.g. `Add Phase 0 skeleton, docs and Git baseline`.
- Body: enough context to understand the change without reading the diff — **not a wall of
  text, not a single vague word**. Explain the *why* when it is not obvious.
- Reference the task id when relevant (e.g. `P0-001`).

Good: `Add backend /health endpoint and health test`
Too small/vague: `fix`, `update`, `stuff`
Too large: a single commit that adds compose, backend, worker and frontend at once.

## What must never be committed

- Real secrets: passwords, access tokens, client secrets, private keys, certificates, private
  connection strings. Only `.env.example` placeholders are committed; `.env` is git-ignored.
- Generated/local artifacts already covered by `.gitignore` (caches, `node_modules/`,
  build output, `local-data/`, logs).

## Branching

- The initial repository baseline is committed on the default branch.
- Subsequent feature/task work should be done on a short-lived branch and merged after review,
  rather than committing feature work directly onto the default branch.

## Before each commit

1. Review the diff (`git status`, `git diff`) — commit only what you intend to.
2. Confirm no secrets or ignored artifacts are staged.
3. Ensure the change is coherent and, where applicable, that its checks/tests pass.
4. Write a message following the rules above.
