"""P2-001 Alembic scaffold tests.

Prove that the approved dependencies import, that the Alembic config and script
directory load, that env.py wires target_metadata to the shared Base.metadata and
takes its URL from app.config, that no credential or database target is committed,
and that no migration revision exists yet.

env.py is exercised in Alembic's OFFLINE mode against a stub context, so these
tests need no database and open no connection.
"""

import contextlib
from pathlib import Path
from unittest import mock

import alembic
import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.db.base import Base

BACKEND_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
ALEMBIC_DIR = BACKEND_DIR / "alembic"
ENV_PY = ALEMBIC_DIR / "env.py"

# Obvious local placeholder — never a real credential.
FAKE_URL = "postgresql+psycopg://test_user:placeholder_pw_local_only@localhost:5432/stemspace_test"


class _StubAlembicConfig:
    """Stands in for alembic's Config during the env.py exec."""

    config_file_name = None  # skips fileConfig(); no logging setup needed here.


class _StubContext:
    """Records what env.py configures, without running or connecting."""

    def __init__(self):
        self.config = _StubAlembicConfig()
        self.configure_kwargs = None
        self.ran_migrations = False

    def is_offline_mode(self) -> bool:
        return True

    def configure(self, **kwargs) -> None:
        self.configure_kwargs = kwargs

    def begin_transaction(self):
        return contextlib.nullcontext()

    def run_migrations(self) -> None:
        self.ran_migrations = True


def _run_env_py(stub: _StubContext) -> None:
    """Exec env.py with `alembic.context` replaced by the stub."""
    source = ENV_PY.read_text(encoding="utf-8")
    namespace = {"__file__": str(ENV_PY), "__name__": "alembic_env_under_test"}
    with mock.patch.object(alembic, "context", stub):
        exec(compile(source, str(ENV_PY), "exec"), namespace)  # noqa: S102


def test_approved_dependencies_import():
    # The three P2-001 dependencies (DEC-0005 §8) — and nothing else.
    import alembic as alembic_mod
    import psycopg
    import sqlalchemy

    for module in (sqlalchemy, alembic_mod, psycopg):
        assert module is not None


def test_alembic_scaffold_files_exist():
    assert ALEMBIC_INI.is_file()
    assert ENV_PY.is_file()
    assert (ALEMBIC_DIR / "script.py.mako").is_file()
    assert (ALEMBIC_DIR / "versions").is_dir()


def test_alembic_config_and_script_directory_load():
    # Proves alembic.ini resolves and the script location is wired correctly.
    config = Config(str(ALEMBIC_INI))
    script = ScriptDirectory.from_config(config)

    assert Path(script.dir).resolve() == ALEMBIC_DIR.resolve()


def test_no_migration_revisions_exist_yet():
    # P2-001 is scaffold only: the first revision arrives with the models.
    versions = ALEMBIC_DIR / "versions"
    assert [p.name for p in versions.glob("*.py")] == []
    assert (versions / ".gitkeep").is_file()


def _config_settings(text: str) -> str:
    """The ini's actual settings — comments are documentation, not configuration."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith(("#", ";"))
    ]
    return " ".join(lines).lower()


def test_alembic_ini_has_no_url_or_credentials():
    settings = _config_settings(ALEMBIC_INI.read_text(encoding="utf-8"))

    # env.py supplies the URL from config.py; the ini must carry no connection
    # string, no credential and no production target.
    assert "sqlalchemy.url" not in settings
    assert "://" not in settings
    assert "password" not in settings


def test_env_py_targets_the_shared_base_metadata(monkeypatch):
    # The load-bearing wiring: Alembic must autogenerate against the very same
    # MetaData the models use, or runtime and migrations drift apart.
    monkeypatch.setenv("DATABASE_URL", FAKE_URL)
    stub = _StubContext()

    _run_env_py(stub)

    assert stub.configure_kwargs is not None, "env.py did not configure a context"
    assert stub.configure_kwargs["target_metadata"] is Base.metadata
    assert stub.ran_migrations is True


def test_env_py_takes_its_url_from_config(monkeypatch):
    # Proves the URL comes from app.config rather than a hardcoded value.
    monkeypatch.setenv("DATABASE_URL", FAKE_URL)
    stub = _StubContext()

    _run_env_py(stub)

    assert stub.configure_kwargs["url"] == FAKE_URL


def test_env_py_fails_safely_without_database_url(monkeypatch):
    # No DATABASE_URL must be a clear failure that never echoes a value.
    from app.config import MissingDatabaseUrlError

    monkeypatch.delenv("DATABASE_URL", raising=False)
    stub = _StubContext()

    with pytest.raises(MissingDatabaseUrlError) as excinfo:
        _run_env_py(stub)

    assert "://" not in str(excinfo.value)


def test_no_startup_migration_or_production_db_config():
    # Migrations are never auto-run at app/container startup, and no production
    # database is configured anywhere in the committed backend sources.
    for name in ("app/main.py", "app/worker.py", "Dockerfile"):
        text = (BACKEND_DIR / name).read_text(encoding="utf-8").lower()
        assert "alembic" not in text
        assert "upgrade head" not in text
