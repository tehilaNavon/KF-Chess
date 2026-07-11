import unittest

from board import Board
from constants import EMPTY_CELL


class TestBoard(unittest.TestCase):
    def test_init_sets_dimensions(self):
        board = Board([["wK", EMPTY_CELL], [EMPTY_CELL, "bP"]])
        self.assertEqual(board.rows, 2)
        self.assertEqual(board.cols, 2)

    def test_get_and_set_cell(self):
        board = Board([[EMPTY_CELL, EMPTY_CELL]])
        board.set_cell(0, 0, "wQ")
        self.assertEqual(board.get_cell(0, 0), "wQ")

    def test_move_piece(self):
        board = Board([[EMPTY_CELL, "wP"], [EMPTY_CELL, EMPTY_CELL]])
        board.move_piece(0, 1, 1, 1)
        self.assertEqual(board.get_cell(0, 1), EMPTY_CELL)
        self.assertEqual(board.get_cell(1, 1), "wP")

    def test_inside_board(self):
        board = Board([[EMPTY_CELL, EMPTY_CELL]])
        self.assertTrue(board.inside_board(0, 0))
        self.assertFalse(board.inside_board(0, 2))


if __name__ == "__main__":
    unittest.main()
