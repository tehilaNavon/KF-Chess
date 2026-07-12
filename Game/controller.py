from constants import CELL_SIZE, EMPTY_CELL
from models import Position


class BoardMapper:
    def __init__(self, cell_size=CELL_SIZE):
        self.cell_size = cell_size

    def to_position(self, x, y):
        return Position(y // self.cell_size, x // self.cell_size)


class Controller:
    def __init__(self, board, game_engine, cell_size=CELL_SIZE):
        self.board = board
        self.game_engine = game_engine
        self.mapper = BoardMapper(cell_size)
        self.selected = None

    def _resolve_position(self, x, y):
        position = self.mapper.to_position(x, y)
        if not self.board.inside_board(position.row, position.col):
            return None
        return position

    def handle_click(self, x, y):
        position = self._resolve_position(x, y)
        if position is None:
            self.selected = None
            return None

        piece = self.board.get_cell(position.row, position.col)

        if self.selected is None:
            if piece != EMPTY_CELL:
                self.selected = position
            return None

        old_position = self.selected
        old_piece = self.board.get_cell(old_position.row, old_position.col)

        if piece != EMPTY_CELL and piece[0] == old_piece[0]:
            self.selected = position
            return None

        result = self.game_engine.request_move(old_position, position)
        self.selected = None
        return result

    def handle_jump(self, x, y):
        position = self._resolve_position(x, y)
        if position is None:
            return None
        return self.game_engine.request_jump(position)

