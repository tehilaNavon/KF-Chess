import unittest

from board import Board
from constants import EMPTY_CELL
from Rules.path_utils import is_path_clear


class TestPathUtils(unittest.TestCase):
    def test_is_path_clear_returns_false_outside_board(self):
        board = Board([[EMPTY_CELL, EMPTY_CELL], [EMPTY_CELL, EMPTY_CELL]])

        self.assertFalse(is_path_clear(board, 0, 0, 5, 5))

    def test_is_path_clear_returns_false_when_path_blocked(self):
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])

        self.assertFalse(is_path_clear(board, 0, 1, 2, 1))

    def test_is_path_clear_returns_true_for_clear_path(self):
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])

        self.assertTrue(is_path_clear(board, 0, 0, 2, 0))


if __name__ == "__main__":
    unittest.main()
