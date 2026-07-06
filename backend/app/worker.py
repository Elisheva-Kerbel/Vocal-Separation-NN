"""StemSpace worker — Phase 0 startup stub.

PHASE 0 BOUNDARY — this is a *startup stub only*. Its single job is to prove the
worker service can import project code and start under Docker Compose. It
deliberately does **not**:

- connect to Redis, PostgreSQL, MinIO / S3, the network or the upload filesystem;
- use Celery / RQ / Dramatiq or any queue / broker / Redis client;
- consume, enqueue or process jobs;
- process audio, run the AI model, or create DB / storage records;
- read or print any secret or connection string.

Real queue wiring (Celery broker, tasks, consumption) arrives in a later,
separately approved phase — not here.

Usage (the worker reuses the backend image under Docker Compose):

- ``python -m app.worker --check`` -> startup smoke check: prints one safe line
  and exits 0. Used by the tests and the Compose one-shot check.
- ``python -m app.worker``         -> long-running stub: prints one safe line and
  then blocks so the container stays alive, with **no** polling loop and **no**
  queue client.
"""

from __future__ import annotations

import argparse
import sys
import threading

# Non-secret worker identity for the log line. Holds no credentials, no URLs,
# no connection strings.
WORKER_NAME = "stemspace-worker"

# The one line the stub prints. Kept free of any secret or connection string so
# worker logs never leak (secrets policy + DEC-0003).
STARTUP_MESSAGE = (
    f"[{WORKER_NAME}] Phase 0 worker startup stub — module imported and started "
    "OK. No queue, no Redis, no job processing yet."
)


def _print_startup() -> None:
    """Emit the single safe startup line (no secrets, no connection strings)."""
    print(STARTUP_MESSAGE, flush=True)


def run_check() -> int:
    """Startup smoke check used by the tests and the Compose one-shot run.

    Confirms the module imports and its entrypoint runs, then returns 0 without
    opening any connection or doing any product work.
    """
    _print_startup()
    return 0


def run_forever() -> None:
    """Long-running stub: keep the container alive without doing product work.

    Blocks on an Event that is never set — no busy-loop, no polling, no queue
    client. Queue consumption is out of Phase 0 scope.
    """
    _print_startup()
    threading.Event().wait()


def main(argv: list[str] | None = None) -> int:
    """Entrypoint. ``--check`` runs the smoke check and exits 0; otherwise the
    process stays alive as the Phase 0 stub."""
    parser = argparse.ArgumentParser(
        prog="app.worker",
        description="StemSpace Phase 0 worker startup stub (no queue processing).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run the startup smoke check and exit 0 (no long-running loop).",
    )
    args = parser.parse_args(argv)

    if args.check:
        return run_check()

    run_forever()
    return 0  # not reached in normal long-running mode (Event never set)


if __name__ == "__main__":
    sys.exit(main())
