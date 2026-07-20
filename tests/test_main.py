import unittest
from unittest.mock import patch

from board import Board
from Display.starting_board import create_standard_starting_board, create_standard_starting_grid
from main import run


class TestMain(unittest.TestCase):
    @patch("main.run_interactive_game")
    def test_run_starts_interactive_game_with_standard_board(self, mock_run_interactive_game):
        run()

        mock_run_interactive_game.assert_called_once()
        board = mock_run_interactive_game.call_args.kwargs["board"]
        self.assertIsInstance(board, Board)
        self.assertEqual(board.grid, create_standard_starting_grid())

    def test_create_standard_starting_board_is_eight_by_eight(self):
        board = create_standard_starting_board()
        self.assertEqual(board.rows, 8)
        self.assertEqual(board.cols, 8)
        self.assertEqual(board.get_cell(0, 4), "bK")
        self.assertEqual(board.get_cell(7, 4), "wK")


if __name__ == "__main__":
    unittest.main()
