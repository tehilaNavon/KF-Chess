import unittest

from board import Board
from constants import EMPTY_CELL
from Game.game_engine import GameEngine
from models import Position


class TestGameEngineMoveRequest(unittest.TestCase):
    def test_request_move_returns_false_when_game_is_over(self):
        """בודק שמנוע המשחק דוחה בקשת תנועה במקרה שהמשחק כבר הסתיים."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        game_engine = GameEngine(board, move_time=1)
        game_engine.is_game_over = True

        result = game_engine.request_move(Position(1, 1), Position(0, 1))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "game_over")

    def test_request_move_rejects_same_square(self):
        """בודק שהמשחק דוחה בקשת תנועה אם המקור והיעד זהים."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        game_engine = GameEngine(board, move_time=1)

        result = game_engine.request_move(Position(1, 1), Position(1, 1))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "same_square")

    def test_request_move_rejects_invalid_premove_for_same_source(self):
        """בודק שפרמשן נוסף מהאותו מקור נדחה כאשר פיסה נמצאת כבר בתנועה."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        game_engine = GameEngine(board, move_time=1)
        game_engine.request_move(Position(1, 1), Position(0, 1))

        result = game_engine.request_move(Position(1, 1), Position(1, 2))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "motion_in_progress")

    def test_request_move_accepts_premove_when_no_conflict(self):
        """בודק שפרמשן חוקי נוסף מאושר אם אין קונפליקט על היעד או המסלול."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", "wN"],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        game_engine = GameEngine(board, move_time=1)
        game_engine.request_move(Position(1, 1), Position(0, 1))

        result = game_engine.request_move(Position(1, 2), Position(2, 0))
        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, "ok")

    def test_request_move_accepts_friendly_landing_after_vacation(self):
        """בודק שתנועה אל משבצת ידידה שמפונה לפני הגעת התנועה מותרת."""
        board = Board([
            [EMPTY_CELL, "wN", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, "wN"],
        ])
        game_engine = GameEngine(board, move_time=1)
        game_engine.request_move(Position(0, 1), Position(2, 0))

        result = game_engine.request_move(Position(2, 2), Position(0, 1))
        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, "ok")

    def test_enemy_later_arrival_captures_at_same_square(self):
        """בודק שאויב שמגיע מאוחר יותר לאותה משבצת אוכל את מי שהגיע קודם."""
        board = Board([
            ["bR", EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            ["wR", EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        game_engine = GameEngine(board, move_time=1)
        game_engine.request_move(Position(0, 0), Position(1, 0))

        result = game_engine.request_move(Position(3, 0), Position(1, 0))
        self.assertTrue(result.is_valid)

        game_engine.advance_time(1)
        self.assertEqual(board.get_cell(1, 0), "bR")

        game_engine.advance_time(2)
        self.assertEqual(board.get_cell(1, 0), "wR")
        self.assertEqual(board.get_cell(0, 0), EMPTY_CELL)
        self.assertEqual(board.get_cell(3, 0), EMPTY_CELL)

    def test_enemy_same_arrival_later_scheduled_captures(self):
        """בודק שבאותו זמן הגעה, האויב שתוזמן שני אוכל את הראשון."""
        board = Board([
            ["bP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL],
            ["wP", EMPTY_CELL],
        ])
        game_engine = GameEngine(board, move_time=1)
        game_engine.request_move(Position(0, 0), Position(1, 0))

        result = game_engine.request_move(Position(2, 0), Position(1, 0))
        self.assertTrue(result.is_valid)

        game_engine.advance_time(1)
        self.assertEqual(board.get_cell(1, 0), "wP")
        self.assertEqual(board.get_cell(0, 0), EMPTY_CELL)
        self.assertEqual(board.get_cell(2, 0), EMPTY_CELL)

    def test_request_move_accepts_valid_move(self):
        """בודק שמסע תקין מבוצע ונכנס לרשימת התנועות הפעילה."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        game_engine = GameEngine(board, move_time=1)

        result = game_engine.request_move(Position(1, 1), Position(0, 1))
        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, "ok")
        self.assertTrue(game_engine.realtime_arbiter.has_active_motion())
