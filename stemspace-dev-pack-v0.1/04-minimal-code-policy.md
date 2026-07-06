# 04 — Minimal Code and No Over-Engineering Policy

Artifact Type: AI Code Agent Pack
Artifact ID: STEMSPACE-DEV-PACK-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff in Pasted text.txt, PRD V1.1 referenced but not directly supplied, role/authority Knowledge Pack v1.1
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact artifact/version before authorized transfer
Execution allowed: No


## Rule

Build the smallest correct implementation for the current approved task.

## Required behavior

- Keep modules focused and explicit.
- Do not add unused hooks, registries, plugins or factories.
- Do not add future abstractions merely because they may be useful later.
- Do not duplicate logic across components, routes or services.
- Add contracts only when another component consumes them.
- Add tests that prove current behavior and prevent known risks.

## Allowed minimal abstractions

Allowed only when directly needed:
- storage adapter in Phase 4 because local MinIO and S3-compatible production must share a safe boundary;
- service layer in backend because routes must stay thin;
- permissions module because security is backend-enforced;
- checkpoint registry in Phase 1 because checkpoint selection must be server-side.

## Not allowed in early phases

- generic provider registry;
- multi-queue routing;
- billing provider abstraction;
- generic admin framework;
- plugin system;
- unapproved MCP/hooks/tools;
- broad UI state management beyond current needs.
