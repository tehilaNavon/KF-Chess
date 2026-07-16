import cv2

from constants import ASSETS_BOARD_PATH, ASSETS_PIECES_ROOT, CELL_SIZE, EMPTY_CELL
from Display.geometry import cell_top_left_pixel, centered_draw_position
from Display.rendering.img import Img
from Display.rendering.sprite_loader import SpriteLoader


class BoardRenderer:
    def __init__(
        self,
        board_image_path=ASSETS_BOARD_PATH,
        pieces_root=ASSETS_PIECES_ROOT,
        cell_size=CELL_SIZE,
    ):
        self._board_image_path = board_image_path
        self._cell_size = cell_size
        self._sprite_loader = SpriteLoader(pieces_root, cell_size)

    def render(self, board):
        canvas = self._create_board_canvas(board.rows, board.cols)
        self._draw_all_pieces(canvas, board)
        return canvas

    def _create_board_canvas(self, row_count, col_count):
        canvas_width = col_count * self._cell_size
        canvas_height = row_count * self._cell_size
        canvas = Img().read(
            self._board_image_path,
            size=(canvas_width, canvas_height),
        )
        self._ensure_rgba(canvas)
        return canvas

    def _ensure_rgba(self, image):
        if image.img.shape[2] == 3:
            image.img = cv2.cvtColor(image.img, cv2.COLOR_BGR2BGRA)

    def _draw_all_pieces(self, canvas, board):
        for row in range(board.rows):
            for col in range(board.cols):
                piece_code = board.get_cell(row, col)
                if piece_code != EMPTY_CELL:
                    self._draw_piece_on_cell(canvas, piece_code, row, col)

    def _draw_piece_on_cell(self, canvas, piece_code, row, col):
        sprite = self._sprite_loader.load_idle_sprite(piece_code)
        cell_x, cell_y = cell_top_left_pixel(row, col, self._cell_size)
        sprite_height, sprite_width = sprite.img.shape[:2]
        draw_x, draw_y = centered_draw_position(
            cell_x,
            cell_y,
            self._cell_size,
            sprite_width,
            sprite_height,
        )
        sprite.draw_on(canvas, draw_x, draw_y)
