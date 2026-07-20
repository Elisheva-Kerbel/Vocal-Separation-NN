"""P2-001 DB base tests.

Prove that the declarative base exposes the one shared metadata, that the DEC-0005
naming convention is present verbatim (so migrations are deterministic), that
importing app.db opens no database connection, and that P2-001 created no domain
entities.
"""

import os
import subprocess
import sys
from pathlib import Path

from app.db import Base
from app.db.base import NAMING_CONVENTION

# DEC-0005 §6 — the naming convention, spelled out here so a silent edit to the
# source fails this test instead of quietly destabilising future migrations.
EXPECTED_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

APP_DIR = Path(__file__).resolve().parents[2] / "app"


def test_base_metadata_exists():
    assert Base.metadata is not None


def test_naming_convention_matches_dec_0005():
    assert NAMING_CONVENTION == EXPECTED_NAMING_CONVENTION


def test_metadata_carries_the_naming_convention():
    # The convention must be on the metadata Alembic targets, not merely defined.
    assert dict(Base.metadata.naming_convention) == EXPECTED_NAMING_CONVENTION


def test_no_domain_models_defined():
    # P2-001 is scaffold only: entities arrive in P2-002, which stays blocked.
    assert Base.metadata.tables == {}
    assert not list(Base.registry.mappers)


def test_no_models_package_exists():
    # A models package would mean P2-002 scope was pulled forward.
    assert not (APP_DIR / "models").exists()


def test_importing_app_db_opens_no_connection():
    # Import must not connect and must not need DATABASE_URL. Connecting is
    # blocked in a fresh interpreter, so any connection attempt at import fails
    # loudly; the engine must also still be uncreated afterwards (lazy, per
    # DEC-0005 §4). Only the connect methods are patched, never the socket class
    # itself — stdlib ssl subclasses socket.socket at import time.
    code = (
        "import socket\n"
        "def _blocked(*args, **kwargs):\n"
        "    raise AssertionError('a network connection was opened at import time')\n"
        "socket.socket.connect = _blocked\n"
        "socket.socket.connect_ex = _blocked\n"
        "socket.create_connection = _blocked\n"
        "import app.db\n"
        "import app.db.session as session\n"
        "assert session._engine is None, 'engine was created at import time'\n"
        "assert session._session_factory is None, 'session factory was created at import time'\n"
    )
    env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}

    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env
    )

    assert result.returncode == 0, f"import opened a connection: {result.stderr}"
