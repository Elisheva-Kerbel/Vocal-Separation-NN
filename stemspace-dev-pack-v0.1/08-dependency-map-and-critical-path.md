# 08 — Dependency Map and Critical Path

Artifact Type: AI Code Agent Pack
Artifact ID: STEMSPACE-DEV-PACK-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff in Pasted text.txt, PRD V1.1 referenced but not directly supplied, role/authority Knowledge Pack v1.1
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact artifact/version before authorized transfer
Execution allowed: No


## Critical path

```text
P0 Dockerized Skeleton
→ P1 AI Benchmark Harness
→ P2 Backend Domain + DB
→ P3 Auth
→ P4 Upload + Private Storage
→ P5 Queue + Worker
→ P6 Result + Secure File Access
→ P7 Quotas + Coupons
→ P8 My Library
→ P9 Public Library
→ P10 Admin RBAC + Audit
→ P11 Settings + Account Deletion
→ P12 QA Hardening
```

## Dependency table

| Package | Depends on | Type | Status | Unlocks |
|---|---|---|---|---|
| P0 | Source handoff + Compose decision | Technical/environment | Draft | P1, P2 |
| P1 | P0 environment + model/checkpoint availability | Technical/test data | Draft | P5 |
| P2 | P0 + approved data entities | Data contract | Draft | P3, P4 |
| P3 | P2 User model + security decisions | Auth/security | Draft | P4 |
| P4 | P2 + P3 + private storage | Storage/security | Draft | P5 |
| P5 | P1 + P4 | Queue/AI/storage | Draft | P6, P7 |
| P6 | P5 + signed URL security | API/security/UX | Draft | P8 |
| P7 | P5 state semantics | Business rules/idempotency | Draft | P8 |
| P8 | P6 + P7 partial | Product/API/UX | Draft | P9 |
| P9 | P8 + Product/UX/legal decisions | Product/UX/security | Do not open yet | P10/P11 dependencies |
| P10 | P9 + RBAC decisions | Security/admin | Do not open yet | QA hardening |
| P11 | P8/P9/P10 decisions | Privacy/security | Draft/blocked | QA hardening |
| P12 | Implemented core flows | QA/evidence | Draft | Release readiness |

## Parallelism

- Phase 1 and Phase 2 may be conditionally parallel after Phase 0 if owned files do not overlap.
- Phase 3+ should be sequential around shared contracts.
- Public/Admin work must remain closed until core private flow is stable.
