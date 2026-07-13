import unittest

from board import Board
from constants import EMPTY_CELL
from Game.controller import Controller
from Game.game_engine import GameEngine
from models import Position


class TestController(unittest.TestCase):
    def setUp(self):
        self.board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        self.game_engine = GameEngine(self.board, move_time=1)
        self.controller = Controller(self.board, self.game_engine)

    def test_controller_selects_piece_on_first_click(self):
        """בודק שלחיצה ראשונה על פיסה בוחרת אותה."""
        result = self.controller.handle_click(100, 100)
        self.assertIsNone(result)
        self.assertEqual(self.controller.selected, Position(1, 1))

    def test_controller_does_not_select_empty_square(self):
        """בודק שלחיצה על משבצת ריקה לא בוחרת כלי."""
        result = self.controller.handle_click(0, 0)
        self.assertIsNone(result)
        self.assertIsNone(self.controller.selected)

    def test_controller_rejects_click_out_of_bounds(self):
        """בודק שלחיצה מחוץ ללוח מאפסת בחירה ומחזירה None."""
        result = self.controller.handle_click(1000, 1000)
        self.assertIsNone(result)
        self.assertIsNone(self.controller.selected)

    def test_controller_requests_move_on_second_click(self):
        """בודק שלחיצה שנייה על משבצת אחרת שולחת בקשת תנועה למנוע המשחק."""
        self.controller.handle_click(100, 100)
        result = self.controller.handle_click(100, 0)
        self.assertTrue(result.is_valid)
        self.assertIsNone(self.controller.selected)

    def test_controller_handle_jump_requests_jump(self):
        """בודק ש-handle_jump שולח בקשת jump למנוע המשחק."""
        result = self.controller.handle_jump(100, 100)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, "ok")

    def test_controller_handle_jump_returns_none_out_of_bounds(self):
        """בודק ש-handle_jump מחוץ ללוח מחזיר None."""
        result = self.controller.handle_jump(1000, 1000)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
