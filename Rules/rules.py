from constants import EMPTY_CELL
from models import Position
from Rules.rules_piece import RULES


class RuleEngine:
    def validate_move(self, board, source, destination, color=None, arrival_time=None, pending_motions=None):
        if not board.inside_board(source.row, source.col) or not board.inside_board(destination.row, destination.col):
            return False, "out_of_bounds"

        if source == destination:
            return False, "same_square"

        piece_code = board.get_cell(source.row, source.col)
        if piece_code == EMPTY_CELL:
            return False, "empty_source"

        destination_code = board.get_cell(destination.row, destination.col)
        color = color or piece_code[0]
        piece_type = piece_code[1]

        if destination_code != EMPTY_CELL and destination_code[0] == color:
            if arrival_time is None or not self._will_destination_be_vacated(destination, arrival_time, pending_motions):
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

    def _will_destination_be_vacated(self, destination, arrival_time, pending_motions):
        if pending_motions is None:
            return False

        for motion in pending_motions:
            if motion.source == destination and motion.arrival_time <= arrival_time:
                return True

        return False
