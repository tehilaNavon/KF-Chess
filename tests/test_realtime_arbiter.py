import unittest

from board import Board
from constants import EMPTY_CELL
from Game.realtime_arbiter import RealTimeArbiter
from models import Position


class TestRealTimeArbiter(unittest.TestCase):
    def test_has_active_motion(self):
        arbiter = RealTimeArbiter(move_time=5)
        self.assertFalse(arbiter.has_active_motion())

        arbiter.start_motion(Position(0, 0), Position(0, 1), 0)
        self.assertTrue(arbiter.has_active_motion())

    def test_advance_time_moves_piece_when_time_arrives(self):
        board = Board([[EMPTY_CELL, EMPTY_CELL], ["wP", EMPTY_CELL]])
        arbiter = RealTimeArbiter(move_time=5)
        arbiter.start_motion(Position(1, 0), Position(0, 0), 0)

        arbiter.advance_time(board, 4)
        self.assertEqual(board.get_cell(1, 0), "wP")

        arbiter.advance_time(board, 5)
        self.assertEqual(board.get_cell(0, 0), "wP")
        self.assertEqual(board.get_cell(1, 0), EMPTY_CELL)


if __name__ == "__main__":
    unittest.main()
