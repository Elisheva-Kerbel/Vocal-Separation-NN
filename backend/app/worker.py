"""StemSpace worker — Celery-based async separation (Phase 5).

Usage:
- ``celery -A app.celery_app worker --loglevel=info -Q separation``
- ``python -m app.worker --check`` -> startup smoke check
- ``python -m app.worker`` -> starts the Celery worker
"""

from __future__ import annotations

import argparse
import sys

WORKER_NAME = "stemspace-worker"
STARTUP_MESSAGE = f"[{WORKER_NAME}] Worker starting — Celery separation queue."


def run_check() -> int:
    print(STARTUP_MESSAGE, flush=True)
    from app.celery_app import celery  # noqa: F401
    print(f"[{WORKER_NAME}] Celery app loaded OK.", flush=True)
    return 0


def run_worker() -> None:
    print(STARTUP_MESSAGE, flush=True)
    from app.celery_app import celery
    import app.tasks  # noqa: F401
    celery.worker_main(["worker", "--loglevel=info", "-Q", "separation", "--concurrency=2"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.worker", description="StemSpace worker.")
    parser.add_argument("--check", action="store_true", help="Smoke check and exit.")
    args = parser.parse_args(argv)

    if args.check:
        return run_check()

    run_worker()
    return 0


if __name__ == "__main__":
    sys.exit(main())
