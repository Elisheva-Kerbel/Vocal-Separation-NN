# DEC-0003 — Private storage only

Status: Draft, pending Nadav/Noa review.

## Decision

All audio files are stored privately.
Frontend never receives storage keys.
Backend grants short-lived signed URLs only after authorization.

## Phase relevance

This decision must be respected from Phase 0 documentation onward and enforced starting in storage/file-access phases.
