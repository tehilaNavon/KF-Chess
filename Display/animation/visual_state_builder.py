from constants import (
    EMPTY_CELL,
    PIECE_STATE_IDLE,
    PIECE_STATE_JUMP,
    PIECE_STATE_LONG_REST,
    PIECE_STATE_MOVE,
    PIECE_STATE_SHORT_REST,
)
from Display.geometry import (
    cell_top_left_pixel,
    centered_draw_position,
    compute_frame_index,
    interpolate_value,
)
from Game.motion_physics import compute_chebyshev_distance, compute_travel_duration_ms
from models import Position


class PieceDrawState:
    def __init__(self, piece_code, pixel_x, pixel_y, state_name, frame_index):
        self.piece_code = piece_code
        self.pixel_x = pixel_x
        self.pixel_y = pixel_y
        self.state_name = state_name
        self.frame_index = frame_index


class VisualStateBuilder:
    def __init__(self, cell_size, piece_config_registry):
        self._cell_size = cell_size
        self._piece_config_registry = piece_config_registry

    def build(self, board, arbiter, current_time):
        hidden_cells = self._collect_hidden_cells(arbiter)
        draw_states = []

        self._append_board_pieces(draw_states, board, arbiter, current_time, hidden_cells)
        self._append_moving_pieces(draw_states, arbiter, current_time)
        self._append_jumping_pieces(draw_states, arbiter, current_time)

        return draw_states

    def _collect_hidden_cells(self, arbiter):
        hidden_cells = set()
        for motion in arbiter.active_motions:
            hidden_cells.add((motion.source.row, motion.source.col))
        for jump in arbiter.active_jumps:
            hidden_cells.add((jump["cell"].row, jump["cell"].col))
        return hidden_cells

    def _append_board_pieces(self, draw_states, board, arbiter, current_time, hidden_cells):
        for row in range(board.rows):
            for col in range(board.cols):
                if (row, col) in hidden_cells:
                    continue
                piece_code = board.get_cell(row, col)
                if piece_code == EMPTY_CELL:
                    continue
                position = Position(row, col)
                draw_states.append(
                    self._build_cell_draw_state(arbiter, current_time, position, piece_code)
                )

    def _build_cell_draw_state(self, arbiter, current_time, position, piece_code):
        rest_state_name = arbiter.piece_rest_registry.get_rest_state_name(position, current_time)
        if rest_state_name in (PIECE_STATE_SHORT_REST, PIECE_STATE_LONG_REST):
            return self._build_rest_draw_state(arbiter, current_time, position, piece_code, rest_state_name)

        pixel_x, pixel_y = self._cell_draw_position(position.row, position.col)
        return self._build_idle_draw_state(piece_code, pixel_x, pixel_y, current_time)

    def _build_idle_draw_state(self, piece_code, pixel_x, pixel_y, current_time):
        idle_config = self._piece_config_registry.get_state_config(piece_code, PIECE_STATE_IDLE)
        frame_index = compute_frame_index(
            current_time,
            idle_config.frames_per_sec,
            idle_config.frame_count,
            idle_config.is_loop,
        ) + 1
        return PieceDrawState(piece_code, pixel_x, pixel_y, PIECE_STATE_IDLE, frame_index)

    def _build_rest_draw_state(self, arbiter, current_time, position, piece_code, rest_state_name):
        rest_config = self._piece_config_registry.get_state_config(piece_code, rest_state_name)
        rest_duration_ms = rest_config.animation_duration_ms()
        elapsed_ms = arbiter.piece_rest_registry.get_rest_elapsed_ms(
            position,
            current_time,
            rest_duration_ms,
        )
        frame_index = compute_frame_index(
            elapsed_ms,
            rest_config.frames_per_sec,
            rest_config.frame_count,
            rest_config.is_loop,
        ) + 1
        pixel_x, pixel_y = self._cell_draw_position(position.row, position.col)
        return PieceDrawState(piece_code, pixel_x, pixel_y, rest_state_name, frame_index)

    def _append_moving_pieces(self, draw_states, arbiter, current_time):
        for motion in arbiter.active_motions:
            draw_states.append(self._build_motion_draw_state(motion, current_time))

    def _build_motion_draw_state(self, motion, current_time):
        move_config = self._piece_config_registry.get_state_config(motion.piece_code, PIECE_STATE_MOVE)
        distance_cells = compute_chebyshev_distance(motion.source, motion.destination)
        travel_duration_ms = compute_travel_duration_ms(distance_cells, move_config.speed_m_per_sec)
        travel_start_time = motion.arrival_time - travel_duration_ms
        elapsed_ms = current_time - travel_start_time
        progress = elapsed_ms / travel_duration_ms if travel_duration_ms > 0 else 1.0
        frame_index = compute_frame_index(
            elapsed_ms,
            move_config.frames_per_sec,
            move_config.frame_count,
            move_config.is_loop,
        ) + 1

        source_x, source_y = self._cell_draw_position(motion.source.row, motion.source.col)
        destination_x, destination_y = self._cell_draw_position(
            motion.destination.row,
            motion.destination.col,
        )
        pixel_x = interpolate_value(source_x, destination_x, progress)
        pixel_y = interpolate_value(source_y, destination_y, progress)
        return PieceDrawState(motion.piece_code, pixel_x, pixel_y, PIECE_STATE_MOVE, frame_index)

    def _append_jumping_pieces(self, draw_states, arbiter, current_time):
        for jump in arbiter.active_jumps:
            draw_states.append(self._build_jump_draw_state(jump, current_time))

    def _build_jump_draw_state(self, jump, current_time):
        piece_code = jump["piece_code"]
        jump_config = self._piece_config_registry.get_state_config(piece_code, PIECE_STATE_JUMP)
        elapsed_ms = current_time - jump["start_time"]
        frame_index = compute_frame_index(
            elapsed_ms,
            jump_config.frames_per_sec,
            jump_config.frame_count,
            jump_config.is_loop,
        ) + 1
        pixel_x, pixel_y = self._cell_draw_position(jump["cell"].row, jump["cell"].col)
        return PieceDrawState(piece_code, pixel_x, pixel_y, PIECE_STATE_JUMP, frame_index)

    def _cell_draw_position(self, row, col):
        cell_x, cell_y = cell_top_left_pixel(row, col, self._cell_size)
        return centered_draw_position(cell_x, cell_y, self._cell_size, self._cell_size, self._cell_size)
