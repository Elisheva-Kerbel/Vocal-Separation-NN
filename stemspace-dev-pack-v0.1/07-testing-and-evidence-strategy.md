# 07 — Testing and Evidence Strategy

Artifact Type: AI Code Agent Pack
Artifact ID: STEMSPACE-DEV-PACK-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff in Pasted text.txt, PRD V1.1 referenced but not directly supplied, role/authority Knowledge Pack v1.1
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact artifact/version before authorized transfer
Execution allowed: No


## Evidence required for every task

- changed files;
- commands/checks run;
- automated test results;
- manual verification;
- known limitations;
- blockers;
- confirmation that no out-of-scope work was performed.

## Phase 0 evidence

- `docker compose config` output or equivalent validation;
- service startup evidence;
- backend `/health` response;
- frontend load evidence;
- worker startup evidence;
- no real secrets;
- no business logic.

## Phase 1 evidence

- benchmark CLI invocation;
- generated vocals file;
- generated background file;
- metrics JSON;
- failure evidence when invalid input is supplied;
- proof that checkpoint path is not client-supplied.

## Phase 2 evidence

- Alembic migration success;
- DB model tests;
- schema serialization tests;
- proof that `storage_key` is not exposed in API schemas.

## Review status

Same-context review is `SELF-REVIEW` and does not replace Nadav.
