import unittest

from board import Board
from constants import EMPTY_CELL
from Game.game_engine import GameEngine
from models import Position


class TestGameEngineGameOver(unittest.TestCase):
    def test_capture_king_ends_game_and_ignores_later_moves(self):
        """בודק שלקיחת מלך מניעה את המשך המשחק ומונעת תנועות נוספות."""
        board = Board([
            ["wK", EMPTY_CELL],
            [EMPTY_CELL, "bQ"],
        ])
        game_engine = GameEngine(board, move_time=1)

        result = game_engine.request_move(Position(1, 1), Position(0, 0))
        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, "ok")

        game_engine.advance_time(1)
        self.assertTrue(game_engine.is_game_over)

        later_result = game_engine.request_move(Position(0, 0), Position(0, 1))
        self.assertFalse(later_result.is_valid)
        self.assertEqual(later_result.reason, "game_over")

    def test_advance_time_updates_current_time(self):
        """בודק שהזמן המתעדכן במנוע משחק משקף את התוספת הניתנת."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        game_engine = GameEngine(board, move_time=1)

        current_time = game_engine.advance_time(10)
        self.assertEqual(current_time, 10)
