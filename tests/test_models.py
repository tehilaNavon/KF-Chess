import unittest

from constants import EMPTY_CELL
from models import Piece, Position


class TestModels(unittest.TestCase):
    def test_position_equality(self):
        self.assertEqual(Position(1, 2), Position(1, 2))
        self.assertNotEqual(Position(1, 2), Position(2, 1))

    def test_piece_from_token(self):
        piece = Piece.from_token("wK")
        self.assertIsNotNone(piece)
        self.assertEqual(piece.color, "w")
        self.assertEqual(piece.kind, "K")

    def test_empty_piece_is_none(self):
        self.assertIsNone(Piece.from_token(EMPTY_CELL))


if __name__ == "__main__":
    unittest.main()
