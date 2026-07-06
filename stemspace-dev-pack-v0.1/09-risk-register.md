# 09 — Risk Register

Artifact Type: AI Code Agent Pack
Artifact ID: STEMSPACE-DEV-PACK-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff in Pasted text.txt, PRD V1.1 referenced but not directly supplied, role/authority Knowledge Pack v1.1
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact artifact/version before authorized transfer
Execution allowed: No


| Risk ID | Risk | Phase | Severity | Mitigation |
|---|---|---|---|---|
| R-001 | Docker environment drifts from real app assumptions | P0 | High | Compose-first, all service URLs by service name. |
| R-002 | Model cannot process real audio reliably | P1 | High | Benchmark harness before API/queue integration. |
| R-003 | Checkpoint path leaks to client | P1/P5 | High | Server-side checkpoint registry only. |
| R-004 | Storage key leaks to frontend | P2/P4/P6 | High | Schema tests and API serialization tests. |
| R-005 | Failed processing counted toward quota | P5/P7 | High | UsageEvent finalization only after Ready. |
| R-006 | Duplicate worker/finalizer double-counts usage | P5/P7 | High | Idempotency and unique success constraints. |
| R-007 | Public/private identity leak | P9 | High | Hidden profile and public API tests. |
| R-008 | Admin role too broad | P10 | High | Scoped RBAC, no generic daily-use admin. |
| R-009 | Over-engineering creates unnecessary complexity | All | Medium | Minimal-code gate in every task. |
| R-010 | Visual drift from Tamar references | UI phases | Medium | Visual fidelity mapping and review. |
