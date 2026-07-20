"""Thin wrapper around the existing game engine.

Single concern: give the server a small, stable surface (advance / move / jump /
read board) over the untouched ``Game`` engine code. All game rules stay in the
original modules; this only adapts, it does not reimplement.
"""

from __future__ import annotations

from typing import Optional

from Display.starting_board import create_standard_starting_board
from Game.game_engine import GameEngine
from models import Position


class EngineAdapter:
    def __init__(self, board=None, move_time: Optional[int] = None) -> None:
        self._board = board or create_standard_starting_board()
        self._engine = GameEngine(self._board, move_time=move_time)

    @property
    def board(self):
        return self._board

    @property
    def engine(self) -> GameEngine:
        return self._engine

    @property
    def is_game_over(self) -> bool:
        return self._engine.is_game_over

    def advance(self, ms: int) -> None:
        self._engine.advance_time(ms)

    def request_move(self, source: Position, destination: Position):
        return self._engine.request_move(source, destination)

    def request_jump(self, source: Position):
        return self._engine.request_jump(source)
