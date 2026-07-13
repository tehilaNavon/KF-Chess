from constants import (
    ERROR_ROW_WIDTH_MISMATCH,
    ERROR_UNKNOWN_TOKEN,
    VALID_TOKENS,
    format_error,
)


def validate(board):
    if board is None or board.rows == 0:
        return None

    width = board.cols
    for r in range(board.rows):
        row = board.get_row(r)
        if len(row) != width:
            return format_error(ERROR_ROW_WIDTH_MISMATCH)

        for token in row:
            if token not in VALID_TOKENS:
                return format_error(ERROR_UNKNOWN_TOKEN)

    return None