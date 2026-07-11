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


if __name__ == "__main__":
    unittest.main()
