# DEC-0002 — Minimal code, no over-engineering

Status: Draft, pending Nadav/technical review.

## Decision

Implement only the smallest correct code required for the current approved task.

## Not allowed

- future abstractions without current use;
- generic plugin/provider systems;
- duplicate logic;
- extra features outside the approved phase.

## Clarification

Minimal code does not mean incomplete features.
It means no unnecessary code inside the current feature scope.
