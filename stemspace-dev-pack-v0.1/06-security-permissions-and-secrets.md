# 06 — Security, Permissions and Secrets

Artifact Type: AI Code Agent Pack
Artifact ID: STEMSPACE-DEV-PACK-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff in Pasted text.txt, PRD V1.1 referenced but not directly supplied, role/authority Knowledge Pack v1.1
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact artifact/version before authorized transfer
Execution allowed: No


## Storage security

- Private storage only.
- No public bucket.
- No public object URLs.
- No permanent file URLs.
- Backend-only authorization before signed URLs.
- Frontend never receives storage keys.
- Signed URLs are not stored in DB.

## Signed URL TTLs

- Download URL: maximum 5 minutes.
- Listen URL: maximum 10 minutes.

## Authorization

Backend must enforce permissions.
UI-only restrictions are insufficient.

## Audit

Audit events required for:
- URL grant;
- publish;
- admin removal;
- account deletion.

## Secrets

Use placeholders only.
Never commit or ask for real credentials in chat, files or repo.
