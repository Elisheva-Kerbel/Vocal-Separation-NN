"""Phase 0 config tests.

Prove that configuration is read under the locked ``S3_*`` names, that credential
values never appear in the settings ``repr`` (no secret exposure), and that the
defaults are safe (no secret baked in).
"""

from app.config import load_settings


def test_load_settings_reads_s3_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://minio:9000")
    monkeypatch.setenv("S3_BUCKET", "stemspace-local-private")
    monkeypatch.setenv("S3_ACCESS_KEY_ID", "local_key_id")
    monkeypatch.setenv("S3_SECRET_ACCESS_KEY", "local_secret_value")

    settings = load_settings()

    assert settings.app_env == "test"
    assert settings.s3_endpoint_url == "http://minio:9000"
    assert settings.s3_bucket == "stemspace-local-private"
    assert settings.s3_access_key_id == "local_key_id"
    assert settings.s3_secret_access_key == "local_secret_value"


def test_settings_repr_hides_credentials(monkeypatch):
    monkeypatch.setenv("S3_ACCESS_KEY_ID", "local_key_id")
    monkeypatch.setenv("S3_SECRET_ACCESS_KEY", "local_secret_value")

    text = repr(load_settings())

    assert "local_secret_value" not in text
    assert "local_key_id" not in text


def test_defaults_are_safe(monkeypatch):
    for var in (
        "APP_ENV",
        "BACKEND_HOST",
        "BACKEND_PORT",
        "S3_ENDPOINT_URL",
        "S3_BUCKET",
        "S3_ACCESS_KEY_ID",
        "S3_SECRET_ACCESS_KEY",
    ):
        monkeypatch.delenv(var, raising=False)

    settings = load_settings()

    assert settings.app_env == "local"
    assert settings.backend_host == "0.0.0.0"
    assert settings.backend_port == 8000
    # No secret is baked into the defaults.
    assert settings.s3_access_key_id == ""
    assert settings.s3_secret_access_key == ""
