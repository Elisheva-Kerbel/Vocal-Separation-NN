# DEC-0003 — Private storage only

Status: **Draft — pending Nadav / Noa (security) review.**

## Decision

All audio files are stored **privately**.

- No public bucket.
- No public object URLs.
- No permanent file URLs.
- The frontend **never** receives storage keys.
- The backend grants **short-lived signed URLs only after an authorization check**
  (backend-enforced; UI-only restrictions are insufficient).
- Signed URLs are not stored in the database.

## Signed URL TTLs (when implemented)

- Download URL: maximum 5 minutes.
- Listen URL: maximum 10 minutes.

## Phase relevance

This decision must be **respected from Phase 0 documentation onward** and **enforced in code**
starting in the storage / file-access phases. Phase 0 itself implements no storage access; it
only records and preserves this boundary.

## Rationale

Audio uploads and separated outputs are user-private assets. Public or permanent URLs would
leak private content and bypass backend authorization, so storage is private and every access
is mediated by a permission-checked, short-lived signed URL.
