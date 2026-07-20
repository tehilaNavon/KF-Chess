import cv2

from constants import (
    ASSETS_BOARD_PATH,
    ASSETS_PIECES_ROOT,
    CELL_SIZE,
    PIECE_STATE_LONG_REST,
    PIECE_STATE_SHORT_REST,
)
from Display.animation.frame_highlight import FrameHighlight
from Display.animation.visual_state_builder import VisualStateBuilder
from Display.geometry import cell_top_left_pixel
from Display.rendering.board_renderer import BoardRenderer

LONG_REST_BORDER_COLOR = (0, 140, 255, 255)
SHORT_REST_BORDER_COLOR = (0, 220, 255, 255)
SELECTED_BORDER_COLOR = (255, 180, 0, 255)
REST_LABEL_COLOR = (255, 255, 255, 255)


class AnimatedBoardRenderer(BoardRenderer):
    def __init__(
        self,
        board_image_path=ASSETS_BOARD_PATH,
        pieces_root=ASSETS_PIECES_ROOT,
        cell_size=CELL_SIZE,
        piece_config_registry=None,
    ):
        super().__init__(board_image_path, pieces_root, cell_size)
        self._piece_config_registry = None
        self._visual_state_builder = None

    def set_piece_config_registry(self, piece_config_registry):
        self._piece_config_registry = piece_config_registry
        self._visual_state_builder = VisualStateBuilder(self._cell_size, piece_config_registry)

    def render(self, board, arbiter, current_time, frame_highlight=None):
        if self._piece_config_registry is None:
            raise ValueError("piece_config_registry is required for animated rendering")
        draw_states = self._visual_state_builder.build(board, arbiter, current_time)
        return self._render_draw_states(board, draw_states, frame_highlight)

    def _render_draw_states(self, board, draw_states, frame_highlight):
        canvas = self._create_board_canvas(board.rows, board.cols)
        for draw_state in draw_states:
            self._draw_piece_state(canvas, draw_state)
        if frame_highlight is not None:
            self._draw_highlights(canvas, frame_highlight)
        return canvas

    def _draw_piece_state(self, canvas, draw_state):
        cached_sprite = self._sprite_loader.load_sprite(
            draw_state.piece_code,
            draw_state.state_name,
            draw_state.frame_index,
        )
        self._draw_sprite_copy_on_canvas(
            canvas,
            cached_sprite,
            int(draw_state.pixel_x),
            int(draw_state.pixel_y),
        )

    def _draw_sprite_copy_on_canvas(self, canvas, cached_sprite, pixel_x, pixel_y):
        from Display.rendering.img import Img

        sprite_copy = Img()
        sprite_copy.img = cached_sprite.img.copy()
        sprite_copy.draw_on(canvas, pixel_x, pixel_y)

    def _draw_highlights(self, canvas, frame_highlight):
        for cell in frame_highlight.selected_cells:
            self._draw_selected_highlight(canvas, cell[0], cell[1])
        for cell, rest_state_name in frame_highlight.resting_cells.items():
            self._draw_rest_highlight(canvas, cell[0], cell[1], rest_state_name)

    def _draw_selected_highlight(self, canvas, row, col):
        self._draw_cell_border(canvas, row, col, SELECTED_BORDER_COLOR, thickness=3)

    def _draw_rest_highlight(self, canvas, row, col, rest_state_name):
        if rest_state_name == PIECE_STATE_LONG_REST:
            border_color = LONG_REST_BORDER_COLOR
            label = "LONG REST"
        else:
            border_color = SHORT_REST_BORDER_COLOR
            label = "SHORT REST"
        self._draw_cell_border(canvas, row, col, border_color, thickness=4)
        self._draw_cell_label(canvas, row, col, label, REST_LABEL_COLOR)

    def _draw_cell_border(self, canvas, row, col, color, thickness):
        cell_x, cell_y = cell_top_left_pixel(row, col, self._cell_size)
        right_x = cell_x + self._cell_size - 1
        bottom_y = cell_y + self._cell_size - 1
        cv2.rectangle(canvas.img, (cell_x, cell_y), (right_x, bottom_y), color[:3], thickness)

    def _draw_cell_label(self, canvas, row, col, label, color):
        cell_x, cell_y = cell_top_left_pixel(row, col, self._cell_size)
        text_x = cell_x + 4
        text_y = cell_y + 18
        cv2.putText(
            canvas.img,
            label,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color[:3],
            1,
            cv2.LINE_AA,
        )
