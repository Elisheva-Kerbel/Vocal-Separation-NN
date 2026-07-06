# Suggested Claude Code / Cursor Prompt Order — Draft Only

Artifact Type: Prompt Plan
Artifact ID: STEMSPACE-PROMPT-ORDER-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Prepared by: Eitan
Required approval: Nadav
Execution allowed: No

## Boundary

This is not an execution instruction.
Use only after Nadav explicitly approves a specific task version for authorized transfer.

## Order

1. Phase 0 / Task P0-001 — Project structure, docs/ and Git baseline.
2. Phase 0 / Task P0-002 — Docker Compose and Dockerfiles.
3. Phase 0 / Task P0-003 — Backend health and config.
4. Phase 0 / Task P0-004 — Worker startup stub.
5. Phase 0 / Task P0-005 — Frontend empty shell.
6. Phase 0 / Task P0-006 — README and coding rules.
7. Review Prompt — Review Phase 0 against acceptance criteria. Do not fix.
8. Phase 1 / Task P1-001 — AI module boundaries.
9. Phase 1 / Task P1-002 — Checkpoint registry and modelTier.
10. Phase 1 / Task P1-003 — Benchmark CLI and metrics.
11. Phase 1 / Task P1-004 — Real audio validation.
12. Phase 2 / Task P2-001 — DB base and Alembic.
13. Phase 2 / Task P2-002 — Domain models.
14. Phase 2 / Task P2-003 — Pydantic schemas and no storage key leak.
15. Phase 2 / Task P2-004 — Seed tags and DB tests.

## Review between prompts

After each implementation task:
- stop;
- return evidence;
- do not continue;
- allow review/fix cycle before the next task.
