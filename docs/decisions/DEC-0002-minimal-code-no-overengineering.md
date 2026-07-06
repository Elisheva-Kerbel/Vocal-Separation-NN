# DEC-0002 — Minimal code, no over-engineering

Status: **Draft — pending Nadav / technical review.**

## Decision

Implement only the **smallest correct code** required for the current approved task.

## Not allowed

- Future abstractions without a current use.
- Generic plugin / provider / registry systems not needed now.
- Multi-queue routing, billing provider abstractions or generic admin frameworks in early
  phases.
- Duplicate logic across components, routes or services.
- Extra features outside the approved phase.
- Broad UI state management beyond current needs.

## Allowed minimal abstractions (only when directly needed)

- Storage adapter, when local MinIO and S3-compatible production must share a safe boundary.
- Backend service layer, so routes stay thin.
- Permissions module, because security is backend-enforced.
- Checkpoint registry, because checkpoint selection must be server-side.

## Clarification

Minimal code does **not** mean incomplete features. It means no unnecessary code inside the
current feature scope: implement only the current task, avoid generic abstractions not needed
now, avoid duplicate logic, and keep routes thin, services focused and schemas explicit.
