"""Phase 0 worker startup-stub tests.

Prove that the worker module imports, that its ``--check`` startup mode exits 0
(the required worker import/start smoke check), and that the startup output leaks
no secrets or connection strings. Also assert the stub pulls in no queue / broker
client, keeping the Phase 0 boundary (no Celery / RQ / Dramatiq / Redis).
"""

import importlib.util
import subprocess
import sys

import app.worker as worker


def test_worker_module_imports():
    # Importing the module and finding its entrypoint proves the worker service
    # can load project code under the backend image.
    assert callable(worker.main)


def test_check_mode_exits_zero(capsys):
    # --check is the startup smoke check: it must run and exit 0.
    exit_code = worker.main(["--check"])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Phase 0 worker startup stub" in out


def test_startup_output_has_no_secrets(capsys):
    # The startup line must never carry a secret or a connection string
    # (secrets policy + DEC-0003).
    worker.main(["--check"])
    out = capsys.readouterr().out.lower()
    for leaked in (
        "secret",
        "password",
        "access_key",
        "s3_",
        "redis://",
        "postgres://",
        "postgresql://",
        "amqp://",
        "database_url",
    ):
        assert leaked not in out


def test_no_queue_client_dependency():
    # Phase 0 forbids Celery / RQ / Dramatiq / a Redis client — none are
    # installed, so the worker cannot be using one.
    for forbidden in ("celery", "redis", "rq", "dramatiq"):
        assert importlib.util.find_spec(forbidden) is None


def test_check_mode_subprocess_exits_zero():
    # The real Compose smoke check, run as a fresh process:
    # `python -m app.worker --check` prints the stub line and exits 0.
    result = subprocess.run(
        [sys.executable, "-m", "app.worker", "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Phase 0 worker startup stub" in result.stdout
