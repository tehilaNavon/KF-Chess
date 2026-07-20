"""Client-side stand-in for the game engine.

The real ``GameEngine`` runs on the server. The existing ``Controller`` only
needs an object exposing ``request_move`` / ``request_jump``; this adapter
implements exactly that surface but, instead of running any rules locally, it
turns each call into a wire command. The server validates and echoes the new
state back as snapshots.

Single concern: translate engine-style calls into network messages.
"""

from __future__ import annotations

from board import Board
from client.ws_client import WSClient
from constants import EMPTY_CELL
from models import Position
from server.protocol.messages import ClientMessage


def _square(position: Position) -> str:
    """Position -> algebraic square, e.g. ``Position(6, 4)`` -> ``e2``."""
    return f"{chr(ord('a') + position.col)}{8 - position.row}"


class RemoteEngine:
    def __init__(self, client: WSClient, board: Board) -> None:
        self._client = client
        self._board = board

    def request_move(self, source: Position, destination: Position):
        piece = self._board.get_cell(source.row, source.col)
        if piece == EMPTY_CELL:
            return None
        command = piece[0].upper() + piece[1].upper() + _square(source) + _square(destination)
        self._client.send(ClientMessage.COMMAND, cmd=command)
        return None

    def request_jump(self, source: Position):
        self._client.send(ClientMessage.JUMP, square=_square(source))
        return None
