"""A single, global game running on the server (no rooms yet).

Responsibilities kept narrow:
- own one EngineAdapter and drive it with a tick loop;
- assign seats (first player = white, second = black, rest = viewers);
- validate that a player only moves their own color;
- broadcast state snapshots over the bus.

It does not read sockets and holds no auth logic.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, Tuple

from constants import EMPTY_CELL
from models import Position
from server.bus import Bus
from server.game.engine_adapter import EngineAdapter
from server.protocol.command_parser import parse_move
from server.protocol.messages import ServerMessage
from server.protocol.state_serializer import serialize_game
from server.session import ROLE_BLACK, ROLE_VIEWER, ROLE_WHITE, Session

logger = logging.getLogger(__name__)

TICK_MS = 16
DEFAULT_SNAPSHOT_INTERVAL_MS = 100

_COLOR_BY_ROLE = {ROLE_WHITE: "w", ROLE_BLACK: "b"}

ERROR_NOT_A_PLAYER = "NOT_A_PLAYER"
ERROR_NOT_YOUR_COLOR = "NOT_YOUR_COLOR"


class LiveGame:
    def __init__(
        self,
        bus: Bus,
        move_time: Optional[int] = None,
        tick_ms: int = TICK_MS,
        snapshot_interval_ms: int = DEFAULT_SNAPSHOT_INTERVAL_MS,
    ) -> None:
        self._bus = bus
        self._adapter = EngineAdapter(move_time=move_time)
        self._tick_ms = tick_ms
        self._snapshot_interval_ms = snapshot_interval_ms
        self._seats: dict[str, Session] = {}
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._ms_since_snapshot = 0
        self._game_over_announced = False

    # --- seating -----------------------------------------------------------
    def assign_seat(self, session: Session) -> str:
        role = self._next_free_role()
        session.role = role
        if role != ROLE_VIEWER:
            self._seats[role] = session
        return role

    def _next_free_role(self) -> str:
        if ROLE_WHITE not in self._seats:
            return ROLE_WHITE
        if ROLE_BLACK not in self._seats:
            return ROLE_BLACK
        return ROLE_VIEWER

    @staticmethod
    def color_of(session: Session) -> Optional[str]:
        return _COLOR_BY_ROLE.get(session.role)

    # --- commands ----------------------------------------------------------
    async def apply_command(self, session: Session, command_text: str) -> Tuple[bool, str]:
        move, error = parse_move(command_text)
        if error is not None:
            return False, error

        player_color = self.color_of(session)
        if player_color is None:
            return False, ERROR_NOT_A_PLAYER
        if move.color != player_color:
            return False, ERROR_NOT_YOUR_COLOR

        result = self._adapter.request_move(move.source, move.destination)
        if not result.is_valid:
            return False, result.reason

        await self._broadcast_snapshot()
        return True, "ok"

    async def apply_jump(self, session: Session, source: Position) -> Tuple[bool, str]:
        player_color = self.color_of(session)
        if player_color is None:
            return False, ERROR_NOT_A_PLAYER

        piece = self._adapter.board.get_cell(source.row, source.col)
        if piece == EMPTY_CELL or piece[0].lower() != player_color:
            return False, ERROR_NOT_YOUR_COLOR

        result = self._adapter.request_jump(source)
        if not result.is_valid:
            return False, result.reason

        await self._broadcast_snapshot()
        return True, "ok"

    # --- state -------------------------------------------------------------
    def snapshot(self) -> dict:
        return serialize_game(self._adapter)

    # --- lifecycle ---------------------------------------------------------
    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        while self._running:
            await asyncio.sleep(self._tick_ms / 1000)
            self._adapter.advance(self._tick_ms)
            await self._maybe_snapshot()
            await self._maybe_announce_game_over()

    async def _maybe_snapshot(self) -> None:
        self._ms_since_snapshot += self._tick_ms
        if self._ms_since_snapshot >= self._snapshot_interval_ms:
            self._ms_since_snapshot = 0
            await self._broadcast_snapshot()

    async def _maybe_announce_game_over(self) -> None:
        if self._adapter.is_game_over and not self._game_over_announced:
            self._game_over_announced = True
            winner_color = self._winner_color()
            await self._bus.emit(
                ServerMessage.GAME_OVER,
                winner=winner_color,
                winner_name=self._winner_name(winner_color),
            )

    async def _broadcast_snapshot(self) -> None:
        await self._bus.emit(ServerMessage.STATE_SNAPSHOT, **self.snapshot())

    def _winner_color(self) -> Optional[str]:
        flat = [cell for row in self._adapter.board.grid for cell in row]
        white_alive = "wK" in flat
        black_alive = "bK" in flat
        if white_alive and not black_alive:
            return "w"
        if black_alive and not white_alive:
            return "b"
        return None

    def _winner_name(self, winner_color: Optional[str]) -> Optional[str]:
        """Map the winning color to the seated player's username, if any."""
        role = {"w": ROLE_WHITE, "b": ROLE_BLACK}.get(winner_color)
        session = self._seats.get(role) if role else None
        if session and session.user is not None:
            return session.user.username
        return None
