EMPTY_CELL = "."
VALID_TOKENS = {
    EMPTY_CELL,
    "wK", "wQ", "wR", "wB", "wN", "wP",
    "bK", "bQ", "bR", "bB", "bN", "bP"
}

CELL_SIZE = 100
MOVE_TIME = 1000
JUMP_DURATION = 1000

COMMAND_PRINT_BOARD = "print board"
COMMAND_WAIT = "wait"
COMMAND_CLICK = "click"
COMMAND_JUMP = "jump"
BOARD_HEADER = "Board:"
COMMANDS_HEADER = "Commands:"

ERROR_ROW_WIDTH_MISMATCH = "ROW_WIDTH_MISMATCH"
ERROR_UNKNOWN_TOKEN = "UNKNOWN_TOKEN"
ERROR_INVALID_ARGUMENT = "INVALID_ARGUMENT"

ERROR_OK = "ok"
ERROR_GAME_OVER = "game_over"
ERROR_MOTION_IN_PROGRESS = "motion_in_progress"
ERROR_EMPTY_SOURCE = "empty_source"
ERROR_OUT_OF_BOUNDS = "out_of_bounds"
ERROR_SAME_SQUARE = "same_square"
ERROR_UNSUPPORTED_PIECE = "unsupported_piece"
ERROR_ILLEGAL_MOVE = "illegal_move"
ERROR_FRIENDLY_PIECE = "friendly_piece"
ERROR_MOVEMENT_CONFLICT = "movement_conflict"
ERROR_ENEMY_COLLISION = "enemy_collision"


def format_error(code):
    return f"ERROR {code}"
