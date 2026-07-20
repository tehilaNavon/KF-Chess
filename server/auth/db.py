"""SQLite lifecycle and schema. Single concern: open/close the database and
create the tables. It knows nothing about auth rules or queries.
"""

from __future__ import annotations

from typing import Optional

import aiosqlite

from server.auth.elo import DEFAULT_RATING

_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash BLOB    NOT NULL,
    salt          BLOB    NOT NULL,
    rating        INTEGER NOT NULL DEFAULT {DEFAULT_RATING},
    games_played  INTEGER NOT NULL DEFAULT 0,
    wins          INTEGER NOT NULL DEFAULT 0,
    losses        INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS matches (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    white_id    INTEGER,
    black_id    INTEGER,
    result      TEXT,
    white_delta INTEGER,
    black_delta INTEGER,
    started_at  TEXT,
    ended_at    TEXT,
    FOREIGN KEY (white_id) REFERENCES users (id),
    FOREIGN KEY (black_id) REFERENCES users (id)
);
"""


class Database:
    """Owns a single aiosqlite connection and the schema."""

    def __init__(self, path: str = ":memory:") -> None:
        self._path = path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        self._connection = await aiosqlite.connect(self._path)
        self._connection.row_factory = aiosqlite.Row
        await self._create_schema()

    async def _create_schema(self) -> None:
        await self.connection.executescript(_SCHEMA)
        await self.connection.commit()

    @property
    def connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError("Database.connect() must be called first")
        return self._connection

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
