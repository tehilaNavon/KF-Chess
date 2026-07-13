from constants import (
    EMPTY_CELL,
    ERROR_EMPTY_SOURCE,
    ERROR_ILLEGAL_MOVE,
    ERROR_OK,
    ERROR_OUT_OF_BOUNDS,
    ERROR_SAME_SQUARE,
    ERROR_UNSUPPORTED_PIECE,
)
from Rules.rules_piece import RULES

class RuleEngine:
    def validate_move(self, board, source, destination, color=None):
        if not board.inside_board(source.row, source.col) or not board.inside_board(destination.row, destination.col):
            return False, ERROR_OUT_OF_BOUNDS

        if source == destination:
            return False, ERROR_SAME_SQUARE

        piece_code = board.get_cell(source.row, source.col)
        if piece_code == EMPTY_CELL:
            return False, ERROR_EMPTY_SOURCE

        color = color or piece_code[0]
        piece_type = piece_code[1]

        dr = abs(destination.row - source.row)
        dc = abs(destination.col - source.col)

        rule = RULES.get(piece_type)
        if rule is None:
            return False, ERROR_UNSUPPORTED_PIECE

        is_legal = rule(board, source.row, source.col, destination.row, destination.col, color, dr, dc)
        if not is_legal:
            return False, ERROR_ILLEGAL_MOVE

        return True, ERROR_OK

