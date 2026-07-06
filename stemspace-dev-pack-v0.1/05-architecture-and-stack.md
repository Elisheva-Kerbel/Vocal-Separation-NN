# 05 — Architecture and Stack

Artifact Type: AI Code Agent Pack
Artifact ID: STEMSPACE-DEV-PACK-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff in Pasted text.txt, PRD V1.1 referenced but not directly supplied, role/authority Knowledge Pack v1.1
Prepared by: Eitan
Required approval: Nadav readiness PASS on this exact artifact/version before authorized transfer
Execution allowed: No


## Local environment

Compose-first local development:

```text
docker-compose.yml
postgres
redis
minio
backend
worker
frontend
```

## Required Docker files

```text
backend/Dockerfile
frontend/Dockerfile
```

The worker should reuse the backend image or a targeted backend build stage to avoid duplicated dependency definitions.

## Required project structure

```text
vocal-removing-platform/
├── README.md
├── .env.example
├── .gitignore
├── .gitattributes
├── .editorconfig
├── docker-compose.yml
├── docs/
│   ├── README.md
│   ├── tasks/
│   │   └── phase-0/
│   ├── prd/
│   ├── architecture/
│   ├── spike/
│   └── decisions/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── app/
│   ├── ai/
│   ├── alembic/
│   ├── scripts/
│   └── tests/
├── infra/
└── local-data/
```

## Git baseline files

Phase 0 must include:
- `.gitignore`;
- `.gitattributes`;
- `.editorconfig`;
- `README.md`;
- `.env.example`;
- `backend/.dockerignore`;
- `frontend/.dockerignore`.

Do not add CI workflows in Phase 0 unless Noa explicitly approves CI/CD scope.
