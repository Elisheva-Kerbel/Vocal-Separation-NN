# 01 — Project Context

Artifact Type: AI Code Agent Pack
Artifact ID: STEMSPACE-DEV-PACK-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff in Pasted text.txt, PRD V1.1 referenced but not directly supplied, role/authority Knowledge Pack v1.1
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact artifact/version before authorized transfer
Execution allowed: No


## Product

Vocal Removing Platform / StemSpace.

## MVP delivery goal

Build a platform where a user can log in, upload audio, process it asynchronously into Vocals + Background, and securely listen/download outputs using short-lived signed URLs.

## First real value flow

```text
Login
→ Upload audio
→ Backend validation
→ Save original to private storage
→ Create Song
→ Create SeparationJob
→ Send job to queue
→ Worker runs AI inference
→ Save Vocals + Background
→ Mark Song Ready
→ User opens Result Page
→ User listens/downloads through signed URL
```

## Current readiness

Ready now for:
- project skeleton;
- architecture-aligned file structure;
- Docker Compose local environment;
- benchmark harness;
- backend foundation;
- frontend foundation;
- isolated phases with acceptance criteria.

Not ready as one big build.

## Phase 0 user update incorporated

Phase 0 must be Compose-first and include:
- `docker-compose.yml`;
- backend and frontend Dockerfiles;
- PostgreSQL, Redis, MinIO, backend, worker and frontend services;
- `docs/` directory with clear Markdown task files;
- minimal Git baseline files.
