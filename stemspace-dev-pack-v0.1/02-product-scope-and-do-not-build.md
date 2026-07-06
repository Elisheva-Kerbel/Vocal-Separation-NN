# 02 — Product Scope and Do Not Build

Artifact Type: AI Code Agent Pack
Artifact ID: STEMSPACE-DEV-PACK-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff in Pasted text.txt, PRD V1.1 referenced but not directly supplied, role/authority Knowledge Pack v1.1
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact artifact/version before authorized transfer
Execution allowed: No


## MVP scope guard

The MVP scope is considered closed based on the supplied handoff, but organizational approval artifacts were not directly supplied in this conversation.

## Do not build now

Do not build:
- full Billing Provider;
- extra stems beyond Vocals + Background;
- mobile native app;
- resumable upload unless later approved;
- public bucket;
- permanent file URLs;
- model execution inside HTTP request;
- generic admin role;
- public by default;
- changes to Free/Pro quotas;
- Public Library before the private core flow works end-to-end;
- Admin before RBAC/security review;
- Billing or payment integration.

## Minimal-code rule

The code must be minimal for the current phase.
Minimal does **not** mean incomplete features.
It means:
- implement only the current task scope;
- avoid generic abstractions not needed now;
- avoid duplicate logic;
- avoid future systems before evidence proves they are needed;
- keep routes thin, services focused and schemas explicit.
