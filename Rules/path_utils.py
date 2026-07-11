from constants import EMPTY_CELL


def is_path_clear(board, r1, c1, r2, c2):
    """Checks whether the path between two cells is empty, excluding the endpoints."""
    if not board.inside_board(r1, c1) or not board.inside_board(r2, c2):
        return False

    dr = r2 - r1
    dc = c2 - c1

    step_r = (dr // abs(dr)) if dr != 0 else 0
    step_c = (dc // abs(dc)) if dc != 0 else 0

    curr_r = r1 + step_r
    curr_c = c1 + step_c

    while (curr_r, curr_c) != (r2, c2):
        if board.get_cell(curr_r, curr_c) != EMPTY_CELL:
            return False
        curr_r += step_r
        curr_c += step_c

    return True
