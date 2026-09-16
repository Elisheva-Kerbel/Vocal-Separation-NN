"""Password hashing — scrypt (DEC-0010 D3).

Everything stdlib: ``hashlib.scrypt`` for passwords, ``hmac.compare_digest``
for comparison.  No passlib/bcrypt/argon2.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

# scrypt cost.  128 * N * r = 16 MB per hash, inside OpenSSL's default 32 MB
# limit, so no maxmem override is needed.
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32
SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Return the self-describing encoded hash of ``password``.

    Format: ``scrypt$n$r$p$<salt-b64>$<hash-b64>``, with a fresh 16-byte random
    salt every call — so the same password never produces the same string twice —
    and the cost parameters carried inline, so they can be raised later without a
    migration.  The plaintext is never stored, logged or returned.
    """
    salt = secrets.token_bytes(SALT_BYTES)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )
    return (
        f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}$"
        f"{base64.b64encode(salt).decode()}${base64.b64encode(derived).decode()}"
    )


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify ``password`` against an encoded hash, in constant time.

    Parameters come from the stored string, not from the constants above, so
    hashes written under older parameters keep verifying.  A malformed, truncated
    or tampered string is a plain ``False`` — never an exception that could
    surface as a traceback.
    """
    try:
        algorithm, n, r, p, salt_b64, hash_b64 = stored_hash.split("$")
        if algorithm != "scrypt":
            return False
        salt = base64.b64decode(salt_b64, validate=True)
        expected = base64.b64decode(hash_b64, validate=True)
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected),
        )
    except (ValueError, TypeError, MemoryError):
        return False
    return hmac.compare_digest(derived, expected)


# Non-enumerating login (D7): an unknown email is verified against this hash, so
# it costs exactly the same scrypt work as a real account.  Derived once from a
# throw-away random password that is never stored, so nothing can match it.
_DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(16))
