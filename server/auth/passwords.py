"""Password hashing. Single concern: turn a password into a safe hash and verify it.

Uses PBKDF2-HMAC-SHA256 from the standard library, so there is no third-party
dependency. Each password gets its own random salt.
"""

from __future__ import annotations

import hashlib
import hmac
import os

_ALGORITHM = "sha256"
_ITERATIONS = 200_000
_SALT_BYTES = 16


def generate_salt() -> bytes:
    """Return a fresh random salt for a new password."""
    return os.urandom(_SALT_BYTES)


def hash_password(password: str, salt: bytes) -> bytes:
    """Derive the hash for ``password`` using ``salt``."""
    return hashlib.pbkdf2_hmac(
        _ALGORITHM,
        password.encode("utf-8"),
        salt,
        _ITERATIONS,
    )


def verify_password(password: str, salt: bytes, expected_hash: bytes) -> bool:
    """Return True if ``password`` matches ``expected_hash`` (constant-time)."""
    candidate = hash_password(password, salt)
    return hmac.compare_digest(candidate, expected_hash)
