from constants import EMPTY_CELL


class Board:

    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows else 0

    def print_board(self):
        for row in self.grid:
            print(" ".join(row))

    def get_cell(self, row, col):
        return self.grid[row][col]

    def set_cell(self, row, col, value):
        self.grid[row][col] = value

    def get_row(self, row):
        return self.grid[row]

    def move_piece(self, r1, c1, r2, c2):
        piece = self.get_cell(r1, c1)
        captured = self.get_cell(r2, c2)
        self.set_cell(r2, c2, piece)
        self.set_cell(r1, c1, EMPTY_CELL)
        return captured

    def inside_board(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols