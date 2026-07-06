# AGENT.md

Artifact Type: AI Code Agent Pack
Artifact ID: STEMSPACE-DEV-PACK-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff in Pasted text.txt, PRD V1.1 referenced but not directly supplied, role/authority Knowledge Pack v1.1
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact artifact/version before authorized transfer
Execution allowed: No


## Agent role

You are an AI code agent operating only after Nadav has approved a specific task version for authorized transfer.

Until that approval exists, all instructions in this pack are planning material only.

## Immutable project boundaries

- Build the MVP in small, testable phases.
- Do not build the full product in one pass.
- Do not open Public Library, Admin, Billing, extra stems, mobile app or resumable upload before their approved phase.
- Private storage only.
- No public bucket or public permanent object URLs.
- Backend-only authorization before signed URLs.
- No AI inference inside the HTTP request.
- One Redis + Celery queue for MVP unless benchmark evidence proves otherwise.
- Minimal code only: no unused abstractions, generic frameworks or future-proofing that is not needed for the current task.

## Technical stack

Frontend:
- React + Vite + JavaScript.
- Mantine UI preferred.
- React Hook Form for forms.
- Zod for validation schemas.
- API calls only through `src/api`.
- No messy inline CSS.
- No business logic inside React components.

Backend:
- Python FastAPI.
- SQLAlchemy models.
- Alembic migrations.
- Pydantic schemas.
- PostgreSQL.
- Redis.
- Celery.
- Pytest.

AI:
- `backend/ai/model.py`
- `backend/ai/inference.py`
- `backend/ai/audio_io.py`
- `backend/ai/metrics.py`
- `backend/ai/checkpoint_registry.py`
- `backend/ai/checkpoints/`
- one inference flow receives `modelTier`.
- checkpoint selection server-side only.
- client never sends checkpoint path, filename or free checkpoint id.

Storage:
- Local dev: MinIO or local storage adapter.
- Production: Cloudflare R2 / S3-compatible storage.
- All files private.
- DB stores only metadata and storage keys.
- Frontend never receives storage key.
- Backend creates signed URL only after permission check.

Queue:
- Redis + Celery.
- One queue for MVP.
- configurable policy/concurrency.
- no separate Professional queue unless benchmark proves need.

## Secrets policy

Never request, commit or print:
- passwords;
- access tokens;
- client secrets;
- private keys;
- certificates;
- private connection strings.

Use placeholders only.

## Stop gate

Stop after the approved task.
Return changed files, checks, evidence, deviations and blockers.
Do not continue to another task.
