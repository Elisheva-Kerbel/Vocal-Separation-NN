# DEC-0001 — Compose-first local development

Status: **Draft — pending Nadav / technical review.**

## Decision

Local development must be **Docker Compose-first**. The database, queue, storage, backend,
worker and frontend are wired together and started consistently from Phase 0.

## Scope

The Compose environment includes these services:

- PostgreSQL
- Redis
- MinIO
- backend
- worker
- frontend

Internal URLs between services use **Compose service names** (e.g. `postgres`, `redis`,
`minio`), not `localhost`.

## Rationale

The DB, queue, storage, backend, worker and frontend must be wired consistently from the very
beginning so that every later phase inherits a stable, reproducible local environment. If the
Compose foundation is wrong, all downstream phases inherit environment instability.

## Consequences

- Phase 0 delivers `docker-compose.yml`, backend/frontend Dockerfiles and `.env.example`
  (in the later Phase 0 tasks P0-002+), plus named volumes for PostgreSQL and MinIO local data.
- No CI/CD in Phase 0 unless the technical authority (Noa) explicitly approves CI/CD scope.
