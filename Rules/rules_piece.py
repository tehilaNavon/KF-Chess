from constants import EMPTY_CELL

from Rules.path_utils import is_path_clear


def king_rule(board, r1, c1, r2, c2, color, dr, dc):#מלך
    return dr <= 1 and dc <= 1


def rook_rule(board, r1, c1, r2, c2, color, dr, dc):#צריח
    return (r1 == r2 or c1 == c2) and is_path_clear(board, r1, c1, r2, c2)


def bishop_rule(board, r1, c1, r2, c2, color, dr, dc):#רץ
    return dr == dc and is_path_clear(board, r1, c1, r2, c2)


def queen_rule(board, r1, c1, r2, c2, color, dr, dc):#מלכה
    return (r1 == r2 or c1 == c2 or dr == dc) and is_path_clear(board, r1, c1, r2, c2)


def knight_rule(board, r1, c1, r2, c2, color, dr, dc):#פרש 
    return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)


def pawn_rule(board, r1, c1, r2, c2, color, dr, dc):#חייל
    direction = -1 if color == "w" else 1
    if color == "w":
        start_row = board.rows - 2 if board.rows > 2 else board.rows - 1
    else:
        start_row = 1 if board.rows > 2 else 0
    final_row = 0 if color == "w" else board.rows - 1

    if c1 == c2:
        if r2 - r1 == direction:
            return board.get_cell(r2, c2) == EMPTY_CELL

        if r2 - r1 == 2 * direction and r1 == start_row:
            intermediate_row = r1 + direction
            return (
                board.get_cell(intermediate_row, c1) == EMPTY_CELL
                and board.get_cell(r2, c2) == EMPTY_CELL
            )

    if dr == 1 and dc == 1 and (r2 - r1 == direction):
        return board.get_cell(r2, c2) != EMPTY_CELL

    return False

     


RULES = {
    "K": king_rule,
    "R": rook_rule,
    "B": bishop_rule,
    "Q": queen_rule,
    "N": knight_rule,
    "P": pawn_rule,
}
