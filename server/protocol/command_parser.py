"""Parse wire move commands like ``WQe2e5`` into board positions.

Single concern: string -> structured move (or an error). No game logic, no
board access; it only translates coordinates.

Format: ``<Color><Piece><fromSquare><toSquare>`` e.g. ``WQe2e5``:
    W  = color (w/b)         Q = piece letter (P,N,B,R,Q,K)
    e2 = from square          e5 = to square

Board orientation (matches the existing starting board):
    row 0 = rank 8 (black back rank at the top), row 7 = rank 1 (white).
    col 0 = file 'a', col 7 = file 'h'.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from models import Position

BOARD_SIZE = 8
VALID_PIECES = "PNBRQK"

ERROR_BAD_FORMAT = "BAD_COMMAND_FORMAT"


@dataclass(frozen=True)
class MoveCommand:
    color: str
    source: Position
    destination: Position


def parse_move(command: str) -> Tuple[Optional[MoveCommand], Optional[str]]:
    """Return ``(MoveCommand, None)`` on success or ``(None, error_code)``."""
    text = command.strip()
    if len(text) != 6:
        return None, ERROR_BAD_FORMAT

    color = text[0].lower()
    piece = text[1].upper()
    if color not in ("w", "b") or piece not in VALID_PIECES:
        return None, ERROR_BAD_FORMAT

    source = parse_square(text[2:4])
    destination = parse_square(text[4:6])
    if source is None or destination is None:
        return None, ERROR_BAD_FORMAT

    return MoveCommand(color, source, destination), None


def parse_square(square: str) -> Optional[Position]:
    """Translate an algebraic square like ``e2`` into a board :class:`Position`."""
    if len(square) != 2:
        return None
    file_char = square[0].lower()
    rank_char = square[1]
    if file_char < "a" or file_char > "h" or not rank_char.isdigit():
        return None

    rank = int(rank_char)
    if not 1 <= rank <= BOARD_SIZE:
        return None

    col = ord(file_char) - ord("a")
    row = BOARD_SIZE - rank
    return Position(row, col)
