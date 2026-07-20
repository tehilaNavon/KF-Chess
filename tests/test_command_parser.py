import unittest

from models import Position
from server.protocol.command_parser import ERROR_BAD_FORMAT, parse_move


class TestCommandParser(unittest.TestCase):
    def test_parses_white_queen_move(self):
        move, error = parse_move("WQe2e5")
        self.assertIsNone(error)
        self.assertEqual(move.color, "w")
        self.assertEqual(move.source, Position(6, 4))       # e2
        self.assertEqual(move.destination, Position(3, 4))  # e5

    def test_parses_black_knight_move(self):
        move, error = parse_move("bNb8c6")
        self.assertIsNone(error)
        self.assertEqual(move.color, "b")
        self.assertEqual(move.source, Position(0, 1))       # b8
        self.assertEqual(move.destination, Position(2, 2))  # c6

    def test_rejects_wrong_length(self):
        _, error = parse_move("WQe2e")
        self.assertEqual(error, ERROR_BAD_FORMAT)

    def test_rejects_bad_color(self):
        _, error = parse_move("XQe2e5")
        self.assertEqual(error, ERROR_BAD_FORMAT)

    def test_rejects_bad_piece(self):
        _, error = parse_move("WZe2e5")
        self.assertEqual(error, ERROR_BAD_FORMAT)

    def test_rejects_off_board_square(self):
        _, error = parse_move("WQe2z9")
        self.assertEqual(error, ERROR_BAD_FORMAT)


if __name__ == "__main__":
    unittest.main()
