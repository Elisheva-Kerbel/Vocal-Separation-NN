# Coding Rules

Status: **Draft — pending Nadav readiness review. Not approved for AI code agent execution.**

These rules adapt `stemspace-dev-pack-v0.1/AGENT.md`, `04-minimal-code-policy.md`,
`05-architecture-and-stack.md` and `06-security-permissions-and-secrets.md` into repo-local
coding rules. They apply to every phase unless a later approved decision changes them.

## 1. Minimal code, no over-engineering

- Build the **smallest correct implementation** for the current approved task.
- Do not add unused hooks, registries, plugins or factories.
- Do not add future abstractions "in case they are useful later".
- Do not duplicate logic across components, routes or services.
- Add a contract/interface only when another component actually consumes it.
- Minimal code does **not** mean incomplete features — implement the current task fully.

Minimal abstractions are allowed **only when directly needed now** (e.g. storage adapter in the
storage phase, backend service layer to keep routes thin, permissions module because security
is backend-enforced, checkpoint registry when checkpoint selection must be server-side).

## 2. Technical stack

**Frontend**
- React + Vite + JavaScript.
- Mantine UI preferred; React Hook Form for forms; Zod for validation schemas.
- API calls **only** through `src/api`. No API logic duplicated elsewhere.
- No business logic inside React components.
- No messy inline CSS.

**Backend**
- Python FastAPI with thin routes.
- Focused service layer; explicit Pydantic schemas.
- SQLAlchemy models and Alembic migrations (in their approved phase).
- PostgreSQL, Redis, Celery.
- Pytest for tests.

**AI (later phases only)**
- Lives under `backend/ai/` (`model.py`, `inference.py`, `audio_io.py`, `metrics.py`,
  `checkpoint_registry.py`, `checkpoints/`).
- One inference flow receives `modelTier`. Checkpoint selection is **server-side only**; the
  client never sends a checkpoint path, filename or free checkpoint id.
- No AI inference inside the HTTP request path.

## 3. Storage and security

- **Private storage only.** No public bucket, no public or permanent object URLs.
- The DB stores only metadata and storage keys. The **frontend never receives storage keys**.
- The backend creates a **signed URL only after a permission check** (backend-enforced
  authorization; UI-only restrictions are insufficient). Signed URLs are not stored in the DB.
- Signed URL TTLs (when implemented): download URL ≤ 5 minutes; listen URL ≤ 10 minutes.
- Local dev storage is MinIO / a local adapter; production is Cloudflare R2 / S3-compatible.

## 4. Queue

- Redis + Celery, **one queue** for the MVP.
- Configurable policy/concurrency. No separate "Professional" queue unless benchmark evidence
  proves the need.

## 5. Secrets

- Never commit, request or print real passwords, access tokens, client secrets, private keys,
  certificates or private connection strings.
- Use **placeholders only** (e.g. `change_me_local_only`). Real values live in a local,
  git-ignored `.env`.

## 6. Configuration

- Internal service URLs use Docker Compose **service names** (`postgres`, `redis`, `minio`),
  not `localhost`.
- Fail safely and visibly on missing/invalid config; do not silently hide config errors.

## 7. Phase 0 boundary — do NOT build

Phase 0 deliberately does **not** build: upload API; queue/job processing; DB domain models;
authentication; AI model execution/inference; billing; admin; public library; public storage;
resumable upload; extra stems beyond Vocals + Background.

## 8. Git workflow

Follow `git-workflow.md` for commit cadence, commit size and message style.

## 9. Status discipline

Repo docs remain **Draft** until Nadav returns a readiness PASS. Do not imply Nadav approval,
and do not continue past the currently approved task's Stop Gate.
