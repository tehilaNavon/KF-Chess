from constants import PIECE_STATE_LONG_REST, PIECE_STATE_SHORT_REST
from models import Position


class FrameHighlight:
    def __init__(self, resting_cells=None, selected_cells=None):
        self.resting_cells = resting_cells or {}
        self.selected_cells = selected_cells or set()


def build_frame_highlight(board, arbiter, current_time):
    resting_cells = {}
    for row in range(board.rows):
        for col in range(board.cols):
            position = Position(row, col)
            rest_state_name = arbiter.piece_rest_registry.get_rest_state_name(position, current_time)
            if rest_state_name in (PIECE_STATE_SHORT_REST, PIECE_STATE_LONG_REST):
                resting_cells[(row, col)] = rest_state_name
    return FrameHighlight(resting_cells=resting_cells)


def with_selected_position(frame_highlight, selected_position):
    selected_cells = set()
    if selected_position is not None:
        selected_cells = {(selected_position.row, selected_position.col)}
    return FrameHighlight(
        resting_cells=frame_highlight.resting_cells,
        selected_cells=selected_cells,
    )
