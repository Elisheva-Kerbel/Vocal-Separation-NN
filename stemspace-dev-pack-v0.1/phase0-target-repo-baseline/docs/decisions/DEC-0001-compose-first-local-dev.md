# DEC-0001 — Compose-first local development

Status: Draft, pending Nadav/technical review.

## Decision

Local development must be Docker Compose-first.

## Scope

Compose includes:
- PostgreSQL
- Redis
- MinIO
- backend
- worker
- frontend

## Rationale

The DB, queue, storage, backend, worker and frontend must be wired consistently from Phase 0.
