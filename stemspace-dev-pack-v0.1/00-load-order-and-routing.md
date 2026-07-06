# 00 — Load Order and Routing

Artifact Type: AI Code Agent Pack
Artifact ID: STEMSPACE-DEV-PACK-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff in Pasted text.txt, PRD V1.1 referenced but not directly supplied, role/authority Knowledge Pack v1.1
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact artifact/version before authorized transfer
Execution allowed: No


## General load order

1. `AGENT.md`
2. `01-project-context.md`
3. `02-product-scope-and-do-not-build.md`
4. Relevant phase file from `/phases`
5. Relevant package file from `/packages`
6. One task file from `/tasks`
7. Relevant prompt from `/prompts`
8. Evidence template from `/templates/evidence-report-template.md`

## Do not load all tasks together

The code agent must receive one approved task at a time.

## Phase-specific load order

### Phase 0

1. `AGENT.md`
2. `phases/PHASE-00-dockerized-project-skeleton.md`
3. `packages/PKG-P0-dockerized-project-skeleton.md`
4. One file from `tasks/phase-0/`
5. `templates/evidence-report-template.md`

### Phase 1

1. `AGENT.md`
2. `phases/PHASE-01-ai-benchmark-harness.md`
3. `packages/PKG-P1-ai-benchmark-harness.md`
4. One file from `tasks/phase-1/`
5. `templates/evidence-report-template.md`

### Phase 2

1. `AGENT.md`
2. `phases/PHASE-02-backend-domain-db-skeleton.md`
3. `packages/PKG-P2-backend-domain-db-skeleton.md`
4. One file from `tasks/phase-2/`
5. `templates/evidence-report-template.md`
