"""Phase 3 local MVP auth tests (DEC-0010 §8).

Covers the crypto helpers as pure functions, the four ``/auth`` routes end to end,
the permission guard, and the binding no-leak properties: no password, encoded
hash, raw session token, ``token_hash``, ``DATABASE_URL``, path or traceback may
appear in any response.

The routes run against an in-memory SQLite database injected through the
``get_db`` dependency (DEC-0008 §5–§7) — no PostgreSQL, no migration run, no
network. ``StaticPool`` keeps the one in-memory database alive across the
connections TestClient's worker thread checks out.
"""

import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import auth
from app.db.base import Base
from app.db.models import User, UserSession
from app.main import app

EMAIL = "singer@example.test"
PASSWORD = "correct horse battery"

# Anything here in a response body would be a leak (DEC-0010 §5). The literal word
# "password" is NOT listed: it is a legitimate request field name. What must never
# appear is the submitted password VALUE, the encoded hash, the raw token and the
# name of any credential column — all of which are checked.
FORBIDDEN_MARKERS = (
    PASSWORD,
    "password_hash",
    "token_hash",
    "scrypt$",
    "stemspace_session",
    "DATABASE_URL",
    "postgresql",
    "secret",
    "Traceback",
    "/app/",
    "sqlite",
)


def assert_no_leak(response):
    body = response.text
    for marker in FORBIDDEN_MARKERS:
        assert marker not in body, f"{marker!r} leaked in {body!r}"


@pytest.fixture
def db_sessions():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine)
    engine.dispose()


@pytest.fixture
def client(db_sessions):
    def override_get_db():
        session = db_sessions()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[auth.get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def db(db_sessions):
    """A direct session, for inspecting stored rows the routes wrote."""
    session = db_sessions()
    yield session
    session.close()


def signup(client, email=EMAIL, password=PASSWORD, **extra):
    return client.post("/auth/signup", json={"email": email, "password": password, **extra})


def login(client, email=EMAIL, password=PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


def make_user(db, email=EMAIL, password=PASSWORD, status="active"):
    user = User(
        email=email,
        status=status,
        password_hash=auth.hash_password(password),
        profile_visibility="hidden",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def session_cookie(client):
    return client.cookies.get(auth.SESSION_COOKIE_NAME)


# --- 1-4. Password hashing helpers -------------------------------------------


def test_hash_and_verify_round_trip():
    assert auth.verify_password(PASSWORD, auth.hash_password(PASSWORD)) is True


def test_same_password_hashes_differently_every_time():
    first, second = auth.hash_password(PASSWORD), auth.hash_password(PASSWORD)
    assert first != second  # random 16-byte salt per hash
    assert auth.verify_password(PASSWORD, first)
    assert auth.verify_password(PASSWORD, second)


def test_wrong_password_is_rejected():
    stored = auth.hash_password(PASSWORD)
    for wrong in ("", "wrong", PASSWORD + " ", PASSWORD.upper()):
        assert auth.verify_password(wrong, stored) is False


def test_encoded_hash_is_self_describing_and_holds_no_plaintext():
    encoded = auth.hash_password(PASSWORD)
    algorithm, n, r, p, salt, digest = encoded.split("$")
    assert (algorithm, int(n), int(r), int(p)) == ("scrypt", 2**14, 8, 1)
    assert salt and digest
    assert PASSWORD not in encoded


@pytest.mark.parametrize(
    "tampered",
    ["", "not-a-hash", "scrypt$16384$8$1$onlyfourparts", "bcrypt$16384$8$1$c2E=$aGE=",
     "scrypt$0$8$1$c2E=$aGE=", "scrypt$16384$8$1$!!!$aGE="],
)
def test_malformed_stored_hash_is_false_not_an_exception(tampered):
    assert auth.verify_password(PASSWORD, tampered) is False


# --- 5. Session tokens: generated, and only the hash is stored ----------------


def test_session_token_is_random_and_only_its_hash_is_storable():
    first, second = auth.create_session_token(), auth.create_session_token()
    assert first != second
    assert len(first) >= 43  # 256 bits, url-safe base64

    digest = auth.hash_session_token(first)
    assert len(digest) == 64 and digest != first
    assert auth.hash_session_token(first) == digest  # deterministic lookup key
    assert auth.hash_session_token(second) != digest


def test_only_the_token_hash_reaches_the_database(client, db):
    assert signup(client).status_code == 201
    token = session_cookie(client)
    stored = db.query(UserSession).one()

    assert stored.token_hash == auth.hash_session_token(token)
    assert token not in stored.token_hash
    assert db.query(UserSession).filter(UserSession.token_hash == token).count() == 0


def test_only_the_password_hash_reaches_the_database(client, db):
    signup(client)
    stored = db.query(User).one()
    assert stored.password_hash.startswith("scrypt$")
    assert PASSWORD not in stored.password_hash
    assert auth.verify_password(PASSWORD, stored.password_hash)


# --- 6. Signup ----------------------------------------------------------------


def test_signup_creates_an_active_user_and_sets_the_cookie(client, db):
    response = signup(client)
    assert response.status_code == 201

    body = response.json()
    assert body["email"] == EMAIL
    assert body["status"] == "active"
    assert body["profileVisibility"] == "hidden"
    assert body["emailOptIn"] is False
    assert set(body) == {
        "id", "email", "status", "profileVisibility", "preferredLanguage", "emailOptIn",
    }
    assert session_cookie(client)
    assert db.query(User).count() == 1
    assert_no_leak(response)


def test_signup_cookie_is_httponly_lax_and_not_in_the_body(client):
    response = signup(client)
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "path=/" in cookie
    assert session_cookie(client) not in response.text


def test_cookie_is_non_secure_only_in_local_dev(monkeypatch):
    # Local dev runs over plain HTTP; every other environment — production
    # included — requires Secure over HTTPS (DEC-0010 D4).
    monkeypatch.setenv("APP_ENV", "local")
    assert auth._cookie_secure() is False
    for env in ("production", "staging", ""):
        monkeypatch.setenv("APP_ENV", env)
        assert auth._cookie_secure() is True


def test_signup_accepts_optional_preferences(client):
    body = signup(
        client, preferredLanguage="he", emailOptIn=True
    ).json()
    assert body["preferredLanguage"] == "he"
    assert body["emailOptIn"] is True


def test_signup_normalises_the_email_and_refuses_a_duplicate(client, db):
    assert signup(client, email=" Singer@Example.TEST ").status_code == 201
    assert db.query(User).one().email == EMAIL

    duplicate = signup(client)
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["error"] == "email_taken"
    assert db.query(User).count() == 1
    assert_no_leak(duplicate)


@pytest.mark.parametrize("bad_email", ["", "not-an-email", "@example.test", " "])
def test_signup_rejects_a_malformed_email_safely(client, bad_email):
    response = signup(client, email=bad_email)
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "invalid_email"
    assert_no_leak(response)


@pytest.mark.parametrize("bad_password", ["short", "x" * 129, "1234567"])
def test_signup_rejects_a_bad_password_without_echoing_it(client, bad_password):
    response = signup(client, password=bad_password)
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "invalid_password"
    assert bad_password not in response.text


@pytest.mark.parametrize(
    "body",
    [
        {"email": EMAIL},                       # password missing
        {"password": PASSWORD},                 # email missing
        {"email": EMAIL, "password": None},     # wrong type
        {"email": EMAIL, "password": {"nested": PASSWORD}},
        {},
    ],
)
def test_incomplete_or_mistyped_credentials_never_echo_the_submitted_value(client, body):
    # A framework validation error would put the offending input in the response;
    # the request models make sure the routes' own safe errors handle these first.
    response = client.post("/auth/signup", json=body)
    assert response.status_code == 400
    assert response.json()["detail"]["error"] in {"invalid_email", "invalid_password"}
    assert_no_leak(response)


# --- 7-8. Login, including the non-enumerating failure ------------------------


def test_login_success_sets_the_cookie(client, db):
    make_user(db)
    response = login(client)
    assert response.status_code == 200
    assert response.json()["email"] == EMAIL
    assert session_cookie(client)
    assert db.query(UserSession).count() == 1
    assert_no_leak(response)


def test_unknown_email_and_wrong_password_are_indistinguishable(client, db):
    make_user(db)
    unknown = login(client, email="nobody@example.test")
    wrong = login(client, password="not-the-password")

    assert unknown.status_code == wrong.status_code == 401
    assert unknown.json() == wrong.json()
    assert unknown.json()["detail"]["error"] == "invalid_credentials"
    assert session_cookie(client) is None
    assert db.query(UserSession).count() == 0
    assert_no_leak(unknown)
    assert_no_leak(wrong)


def test_failed_login_creates_no_session(client, db):
    make_user(db)
    login(client, password="nope")
    assert db.query(UserSession).count() == 0


# --- 9-10. /auth/me and the guard --------------------------------------------


def test_me_returns_the_user_with_a_cookie(client, db):
    make_user(db)
    login(client)
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == EMAIL
    assert_no_leak(response)


def test_me_without_a_cookie_is_401(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "not_authenticated"
    assert_no_leak(response)


def test_me_with_an_unknown_cookie_is_401(client):
    client.cookies.set(auth.SESSION_COOKIE_NAME, auth.create_session_token())
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert_no_leak(response)


def test_expired_session_is_401_and_the_row_is_deleted(client, db):
    user = make_user(db)
    token = auth.create_session_token()
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=auth.hash_session_token(token),
            expires_at=datetime.datetime.now(datetime.timezone.utc)
            - datetime.timedelta(minutes=1),
        )
    )
    db.commit()

    client.cookies.set(auth.SESSION_COOKIE_NAME, token)
    response = client.get("/auth/me")
    assert response.status_code == 401
    # Lazy cleanup (DEC-0010 D5): the expired row is gone, with no sweeper.
    assert db.query(UserSession).count() == 0
    assert_no_leak(response)


def test_session_lifetime_is_seven_days(client, db):
    make_user(db)
    login(client)
    stored = db.query(UserSession).one()
    created = stored.created_at.replace(tzinfo=None)
    assert stored.expires_at.replace(tzinfo=None) - created >= datetime.timedelta(days=6)
    assert stored.expires_at.replace(tzinfo=None) - created <= datetime.timedelta(days=8)


# --- 11. Logout ---------------------------------------------------------------


def test_logout_deletes_the_session_and_clears_the_cookie(client, db):
    make_user(db)
    login(client)
    assert db.query(UserSession).count() == 1

    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Signed out."}
    assert db.query(UserSession).count() == 0
    assert not session_cookie(client)
    assert client.get("/auth/me").status_code == 401
    assert_no_leak(response)


def test_logout_without_a_session_is_safe_and_idempotent(client):
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Signed out."}
    assert_no_leak(response)


# --- 12-14. Blocked and deleted accounts --------------------------------------


@pytest.mark.parametrize("status", ["blocked", "deleted"])
def test_blocked_or_deleted_user_cannot_login(client, db, status):
    make_user(db, status=status)
    response = login(client)
    assert response.status_code == 401
    # Identical to an unknown account: status is not disclosed either (D7).
    assert response.json()["detail"]["error"] == "invalid_credentials"
    assert db.query(UserSession).count() == 0
    assert_no_leak(response)


@pytest.mark.parametrize("status", ["blocked", "deleted"])
def test_existing_session_stops_working_when_the_user_is_blocked(client, db, status):
    user = make_user(db)
    login(client)
    assert client.get("/auth/me").status_code == 200

    user.status = status
    db.commit()

    response = client.get("/auth/me")
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "account_not_active"
    assert_no_leak(response)


# --- 15. Aggregate no-leak sweep ---------------------------------------------


def test_no_auth_response_leaks_a_credential_token_or_path(client, db):
    make_user(db, email="other@example.test")
    responses = [
        signup(client),
        signup(client),
        signup(client, email="bad", password=PASSWORD),
        signup(client, password="x"),
        login(client, email="other@example.test"),
        login(client, email="nobody@example.test"),
        login(client, password="wrong"),
        client.get("/auth/me"),
        client.post("/auth/logout"),
        client.get("/auth/me"),
        client.post("/auth/signup", json={"email": EMAIL}),
        client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD, "extra": 1}),
    ]
    for response in responses:
        assert_no_leak(response)


def test_auth_module_imports_no_auth_library_and_no_new_dependency():
    # DEC-0010 D3: stdlib only. Checked against the module's import statements —
    # the prose above them names the rejected alternatives on purpose.
    from pathlib import Path

    imports = [
        line.strip().lower()
        for line in Path(auth.__file__).read_text(encoding="utf-8").splitlines()
        if line.startswith(("import ", "from "))
    ]
    for forbidden in ("passlib", "bcrypt", "argon2", "jose", "jwt", "oauth", "authlib"):
        assert not any(forbidden in line for line in imports), forbidden
    # Everything imported is either stdlib or an already-approved dependency.
    allowed_roots = {
        "base64", "datetime", "hashlib", "hmac", "secrets", "uuid", "typing",
        "__future__", "fastapi", "pydantic", "sqlalchemy", "app",
    }
    for line in imports:
        root = line.split()[1].split(".")[0]
        assert root in allowed_roots, f"unexpected import: {line}"


def test_demo_routes_stay_open_and_unauthenticated(client):
    # Phase 3 adds accounts, not a gate on the Fast Demo (DEC-0010 §6).
    response = client.post(
        "/demo/separate", content=b"", headers={"content-type": "audio/wav"}
    )
    assert response.status_code == 400  # empty body, not 401/403
    assert response.json()["error"] == "empty_body"
