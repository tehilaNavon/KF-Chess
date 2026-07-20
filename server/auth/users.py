"""User row storage. Single concern: read/write the ``users`` table.

Contains no auth rules and no password logic - just queries. Each method does
exactly one database operation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import aiosqlite

from server.auth.db import Database


@dataclass(frozen=True)
class UserRecord:
    id: int
    username: str
    password_hash: bytes
    salt: bytes
    rating: int
    games_played: int
    wins: int
    losses: int


def _to_record(row: aiosqlite.Row) -> UserRecord:
    return UserRecord(
        id=row["id"],
        username=row["username"],
        password_hash=row["password_hash"],
        salt=row["salt"],
        rating=row["rating"],
        games_played=row["games_played"],
        wins=row["wins"],
        losses=row["losses"],
    )


class UserStore:
    """CRUD for user records."""

    def __init__(self, database: Database) -> None:
        self._db = database

    async def create(self, username: str, password_hash: bytes, salt: bytes) -> UserRecord:
        """Insert a new user (rating defaults to 1200) and return it."""
        cursor = await self._db.connection.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt),
        )
        await self._db.connection.commit()
        created = await self.get_by_id(cursor.lastrowid)
        assert created is not None
        return created

    async def get_by_username(self, username: str) -> Optional[UserRecord]:
        async with self._db.connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ) as cursor:
            row = await cursor.fetchone()
        return _to_record(row) if row else None

    async def get_by_id(self, user_id: int) -> Optional[UserRecord]:
        async with self._db.connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
        return _to_record(row) if row else None

    async def exists(self, username: str) -> bool:
        async with self._db.connection.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (username,),
        ) as cursor:
            return await cursor.fetchone() is not None

    async def record_result(self, user_id: int, rating: int, won: bool) -> None:
        """Update rating and win/loss counters after a finished game."""
        await self._db.connection.execute(
            """
            UPDATE users
               SET rating = ?,
                   games_played = games_played + 1,
                   wins = wins + ?,
                   losses = losses + ?
             WHERE id = ?
            """,
            (rating, 1 if won else 0, 0 if won else 1, user_id),
        )
        await self._db.connection.commit()
