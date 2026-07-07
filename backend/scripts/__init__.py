"""Backend developer/benchmark scripts (Phase 1).

Local-only command-line tools that live outside the FastAPI app and worker. They
connect to no external system (no upload API, DB, queue, Redis or S3/MinIO). The
Phase 1 benchmark CLI is :mod:`scripts.run_benchmark`.
"""
