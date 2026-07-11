import unittest

from board import Board
from constants import EMPTY_CELL
from Game.controller import Controller
from Game.game_engine import GameEngine
from models import Position


class TestGameLogic(unittest.TestCase):
    def setUp(self):
        self.board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        self.game_engine = GameEngine(self.board, move_time=1)
        self.controller = Controller(self.board, self.game_engine)

    def test_request_move_returns_false_when_game_is_over(self):
        """בודק שמנוע המשחק מונע תנועה אם המשחק כבר הסתיים."""
        self.game_engine.is_game_over = True
        result = self.game_engine.request_move(Position(1, 1), Position(0, 1))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "game_over")

    def test_request_move_rejects_same_square(self):
        """בודק שמסע לאותו המיקום נדחה."""
        result = self.game_engine.request_move(Position(1, 1), Position(1, 1))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "same_square")

    def test_request_move_rejects_when_motion_is_already_active(self):
        """בודק שמסע חדש נדחה אם יש כבר תנועה פעילה."""
        self.game_engine.request_move(Position(1, 1), Position(0, 1))
        result = self.game_engine.request_move(Position(0, 1), Position(0, 0))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "motion_in_progress")

    def test_request_move_accepts_valid_move(self):
        """בודק שמסע חוקי מאושר ומתחיל תנועה."""
        result = self.game_engine.request_move(Position(1, 1), Position(0, 1))
        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, "ok")
        self.assertTrue(self.game_engine.realtime_arbiter.has_active_motion())

    def test_advance_time_updates_current_time(self):
        """בודק שהזמן מתעדכן כראוי כאשר מעבירים את המנוע."""
        current_time = self.game_engine.advance_time(10)
        self.assertEqual(current_time, 10)

    def test_controller_selects_piece_on_first_click(self):
        """בודק שלחיצה ראשונה על משבצת עם כלי בוחרת את הכלי."""
        result = self.controller.handle_click(100, 100)
        self.assertIsNone(result)
        self.assertEqual(self.controller.selected, Position(1, 1))

    def test_controller_does_not_select_empty_square(self):
        """בודק שלחיצה על משבצת ריקה לא בוחרת דבר."""
        result = self.controller.handle_click(0, 0)
        self.assertIsNone(result)
        self.assertIsNone(self.controller.selected)

    def test_controller_rejects_click_out_of_bounds(self):
        """בודק שלחיצה מחוץ ללוח מאופסת ומחזירה None."""
        result = self.controller.handle_click(1000, 1000)
        self.assertIsNone(result)
        self.assertIsNone(self.controller.selected)

    def test_controller_requests_move_on_second_click(self):
        """בודק שלחיצה שנייה על משבצת אחרת מבצעת בקשת תנועה."""
        self.controller.handle_click(100, 100)
        result = self.controller.handle_click(100, 0)
        self.assertTrue(result.is_valid)
        self.assertIsNone(self.controller.selected)


if __name__ == "__main__":
    unittest.main()
