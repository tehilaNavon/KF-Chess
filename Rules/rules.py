from constants import EMPTY_CELL
from models import Position
from Rules.rules_piece import RULES


class RuleEngine:
    def validate_move(self, board, source, destination):
        if not board.inside_board(source.row, source.col) or not board.inside_board(destination.row, destination.col):
            return False, "out_of_bounds"

        if source == destination:
            return False, "same_square"

        piece_code = board.get_cell(source.row, source.col)
        if piece_code == EMPTY_CELL:
            return False, "empty_source"

        destination_code = board.get_cell(destination.row, destination.col)
        color, piece_type = piece_code[0], piece_code[1]

        if destination_code != EMPTY_CELL and destination_code[0] == color:
            return False, "friendly_piece"

        dr = abs(destination.row - source.row)
        dc = abs(destination.col - source.col)

        rule = RULES.get(piece_type)
        if rule is None:
            return False, "unsupported_piece"

        is_legal = rule(board, source.row, source.col, destination.row, destination.col, color, dr, dc)
        if not is_legal:
            return False, "illegal_move"

        return True, "ok"
