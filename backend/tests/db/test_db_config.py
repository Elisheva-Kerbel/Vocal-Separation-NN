"""P2-001 DB config tests.

Prove that the DB URL is read through app.config (the single DB-URL source), that
it never leaks into a repr or an error message, that a missing DATABASE_URL fails
clearly instead of silently falling back, and that no database target is baked
into the defaults.
"""

import pytest

from app.config import MissingDatabaseUrlError, load_settings, require_database_url

# Obvious local placeholders — never a real credential (docs/coding-rules.md §5).
FAKE_PASSWORD = "placeholder_pw_local_only"
FAKE_URL = f"postgresql+psycopg://test_user:{FAKE_PASSWORD}@localhost:5432/stemspace_test"


def test_load_settings_reads_database_url(monkeypatch):
    # DATABASE_URL is read by config.py, so DB modules never call os.getenv.
    monkeypatch.setenv("DATABASE_URL", FAKE_URL)

    assert load_settings().database_url == FAKE_URL


def test_database_url_is_repr_hidden(monkeypatch):
    # The URL embeds a password: it must not appear in the settings repr, which
    # is what ends up in logs and tracebacks.
    monkeypatch.setenv("DATABASE_URL", FAKE_URL)

    text = repr(load_settings())

    assert FAKE_URL not in text
    assert FAKE_PASSWORD not in text
    assert "database_url" not in text


def test_require_database_url_returns_configured_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", FAKE_URL)

    assert require_database_url() == FAKE_URL


@pytest.mark.parametrize("value", ["", "   "])
def test_missing_database_url_fails_safely(monkeypatch, value):
    # Missing/blank must be a clear, visible failure — not a silent fallback and
    # not a default connection target.
    monkeypatch.setenv("DATABASE_URL", value)

    with pytest.raises(MissingDatabaseUrlError) as excinfo:
        require_database_url()

    assert "DATABASE_URL" in str(excinfo.value)


def test_missing_database_url_error_does_not_echo_url_or_password(monkeypatch):
    # DEC-0005 §7: the error names the variable, never its value.
    monkeypatch.setenv("DATABASE_URL", "   ")

    with pytest.raises(MissingDatabaseUrlError) as excinfo:
        require_database_url()

    message = str(excinfo.value)
    assert FAKE_PASSWORD not in message
    assert "postgresql" not in message
    assert "://" not in message


def test_unset_database_url_fails_safely(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(MissingDatabaseUrlError):
        require_database_url()


def test_no_database_target_is_baked_into_defaults(monkeypatch):
    # No production (or any) DB URL is hardcoded, and loading config without a
    # DATABASE_URL must NOT raise — /health and every non-DB path depend on that.
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert load_settings().database_url == ""
