import unittest
from unittest.mock import patch

from board import Board
from parser import parse_input
from validator import validate


class TestParserValidator(unittest.TestCase):
    @patch("builtins.input", side_effect=["Board:", "wK .", ". bP", "Commands:", "print board", "wait 10", EOFError()])
    def test_parse_input_reads_board_and_commands(self, _mock_input):
        board, commands = parse_input()
        self.assertEqual(board.get_cell(0, 0), "wK")
        self.assertEqual(board.get_cell(1, 1), "bP")
        self.assertEqual(commands, ["print board", "wait 10"])

    def test_validate_accepts_valid_board(self):
        board = Board([["wK", "."], [".", "bP"]])
        self.assertIsNone(validate(board))

    def test_validate_rejects_unknown_token(self):
        board = Board([["xK", "."]])
        self.assertEqual(validate(board), "ERROR UNKNOWN_TOKEN")

    def test_validate_returns_none_for_empty_board(self):
        board = Board([])
        self.assertIsNone(validate(board))

    def test_validate_rejects_row_width_mismatch(self):
        board = Board([["wK", "."], ["bP"]])
        self.assertEqual(validate(board), "ERROR ROW_WIDTH_MISMATCH")


if __name__ == "__main__":
    unittest.main()
