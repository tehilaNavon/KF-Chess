import unittest

from board import Board
from constants import EMPTY_CELL
from models import Position
from Rules.rules import RuleEngine


class TestRules(unittest.TestCase):
    def setUp(self):
        self.board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP"],
        ])
        self.engine = RuleEngine()

    def test_valid_pawn_move(self):
        valid, reason = self.engine.validate_move(self.board, Position(1, 1), Position(0, 1))
        self.assertTrue(valid)
        self.assertEqual(reason, "ok")

    def test_same_square_is_invalid(self):
        valid, reason = self.engine.validate_move(self.board, Position(1, 1), Position(1, 1))
        self.assertFalse(valid)
        self.assertEqual(reason, "same_square")

    def test_empty_source_is_invalid(self):
        valid, reason = self.engine.validate_move(self.board, Position(0, 0), Position(0, 1))
        self.assertFalse(valid)
        self.assertEqual(reason, "empty_source")


if __name__ == "__main__":
    unittest.main()
