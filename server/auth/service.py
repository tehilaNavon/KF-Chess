"""Authentication rules. Single concern: register and login.

Orchestrates the smaller pieces (password hashing + user store) but holds no SQL
and no crypto details of its own.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from server.auth import passwords
from server.auth.users import UserRecord, UserStore

ERROR_INVALID_INPUT = "INVALID_INPUT"
ERROR_USERNAME_TAKEN = "USERNAME_TAKEN"
ERROR_INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

MIN_USERNAME_LEN = 3
MIN_PASSWORD_LEN = 4


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    user: Optional[UserRecord] = None
    error: Optional[str] = None


class AuthService:
    def __init__(self, users: UserStore) -> None:
        self._users = users

    async def register(self, username: str, password: str) -> AuthResult:
        if not self._is_valid_input(username, password):
            return AuthResult(ok=False, error=ERROR_INVALID_INPUT)
        if await self._users.exists(username):
            return AuthResult(ok=False, error=ERROR_USERNAME_TAKEN)

        salt = passwords.generate_salt()
        password_hash = passwords.hash_password(password, salt)
        user = await self._users.create(username, password_hash, salt)
        return AuthResult(ok=True, user=user)

    async def login(self, username: str, password: str) -> AuthResult:
        user = await self._users.get_by_username(username)
        if user is None:
            return AuthResult(ok=False, error=ERROR_INVALID_CREDENTIALS)
        if not passwords.verify_password(password, user.salt, user.password_hash):
            return AuthResult(ok=False, error=ERROR_INVALID_CREDENTIALS)
        return AuthResult(ok=True, user=user)

    @staticmethod
    def _is_valid_input(username: str, password: str) -> bool:
        return (
            isinstance(username, str)
            and isinstance(password, str)
            and len(username.strip()) >= MIN_USERNAME_LEN
            and len(password) >= MIN_PASSWORD_LEN
        )
