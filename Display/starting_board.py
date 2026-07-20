from constants import EMPTY_CELL
from board import Board


def create_standard_starting_grid():
    empty_row = [EMPTY_CELL] * 8
    black_pawn_row = ["bP"] * 8
    white_pawn_row = ["wP"] * 8
    black_back_row = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"]
    white_back_row = ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]

    return [
        black_back_row,
        black_pawn_row,
        empty_row.copy(),
        empty_row.copy(),
        empty_row.copy(),
        empty_row.copy(),
        white_pawn_row,
        white_back_row,
    ]


def create_standard_starting_board():
    return Board(create_standard_starting_grid())
