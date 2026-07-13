import unittest

from board import Board
from constants import EMPTY_CELL
from Game.realtime_arbiter import RealTimeArbiter
from models import Position


class TestRealTimeArbiter(unittest.TestCase):
    def test_has_active_motion(self):
        arbiter = RealTimeArbiter(move_time=5)
        self.assertFalse(arbiter.has_active_motion())

        arbiter.start_motion(Position(0, 0), Position(0, 1), 0, "wP")
        self.assertTrue(arbiter.has_active_motion())

    def test_advance_time_moves_piece_when_time_arrives(self):
        board = Board([[EMPTY_CELL, EMPTY_CELL], ["wP", EMPTY_CELL]])
        arbiter = RealTimeArbiter(move_time=5)
        arbiter.start_motion(Position(1, 0), Position(0, 0), 0, "wP")

        arbiter.advance_time(board, 4)
        self.assertEqual(board.get_cell(1, 0), "wP")

        arbiter.advance_time(board, 5)
        self.assertEqual(board.get_cell(0, 0), "wP")
        self.assertEqual(board.get_cell(1, 0), EMPTY_CELL)

    def test_advance_time_later_enemy_captures_at_same_square(self):
        """בודק שבהגעה מאוחרת יותר לאותה משבצת, האויב אוכל את הכלי שכבר שם."""
        board = Board([
            ["bR", EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            ["wR", EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        arbiter = RealTimeArbiter(move_time=1)
        arbiter.start_motion(Position(0, 0), Position(1, 0), 0, "bR")
        arbiter.start_motion(Position(3, 0), Position(1, 0), 0, "wR")

        arbiter.advance_time(board, 1)
        self.assertEqual(board.get_cell(1, 0), "bR")

        arbiter.advance_time(board, 2)
        self.assertEqual(board.get_cell(1, 0), "wR")

    def test_can_schedule_motion_allows_enemy_same_destination(self):
        """בודק ששני אויבים יכולים לתזמן תנועה לאותה משבצת."""
        board = Board([
            ["bP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL],
            ["wP", EMPTY_CELL],
        ])
        arbiter = RealTimeArbiter(move_time=1)
        arbiter.start_motion(Position(0, 0), Position(1, 0), 0, "bP")

        can_schedule, reason = arbiter.can_schedule_motion(
            board, Position(2, 0), Position(1, 0), 0, "wP"
        )
        self.assertTrue(can_schedule)
        self.assertEqual(reason, "ok")

    def test_can_schedule_motion_rejects_source_in_motion(self):
        """בודק שלא ניתן לתזמן תנועה מכלי שכבר בתנועה."""
        board = Board([[EMPTY_CELL, "wP"], [EMPTY_CELL, EMPTY_CELL]])
        arbiter = RealTimeArbiter(move_time=1)
        arbiter.start_motion(Position(0, 1), Position(1, 1), 0, "wP")

        can_schedule, reason = arbiter.can_schedule_motion(
            board, Position(0, 1), Position(0, 0), 0, "wP"
        )
        self.assertFalse(can_schedule)
        self.assertEqual(reason, "motion_in_progress")

    def test_can_schedule_motion_rejects_friendly_piece_on_destination(self):
        """בודק שלא ניתן לתזמן תנועה למשבצת תפוסה בידיד."""
        board = Board([[EMPTY_CELL, "wN"], [EMPTY_CELL, "wP"]])
        arbiter = RealTimeArbiter(move_time=1)

        can_schedule, reason = arbiter.can_schedule_motion(
            board, Position(1, 1), Position(0, 1), 0, "wP"
        )
        self.assertFalse(can_schedule)
        self.assertEqual(reason, "friendly_piece")

    def test_can_schedule_motion_allows_destination_that_will_vacate(self):
        """בודק שניתן לתזמן תנועה למשבצת ידיד שתתפנה לפני ההגעה."""
        board = Board([
            [EMPTY_CELL, "wN", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, "wP"],
        ])
        arbiter = RealTimeArbiter(move_time=1)
        arbiter.start_motion(Position(0, 1), Position(2, 0), 0, "wN")

        can_schedule, reason = arbiter.can_schedule_motion(
            board, Position(2, 2), Position(0, 1), 0, "wP"
        )
        self.assertTrue(can_schedule)
        self.assertEqual(reason, "ok")

    def test_can_schedule_motion_rejects_friendly_same_destination(self):
        """בודק ששני ידידים לאותה משבצת נדחים."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", "wN"],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])
        arbiter = RealTimeArbiter(move_time=1)
        arbiter.start_motion(Position(1, 1), Position(0, 1), 0, "wP")

        can_schedule, reason = arbiter.can_schedule_motion(
            board, Position(1, 2), Position(0, 1), 0, "wN"
        )
        self.assertFalse(can_schedule)
        self.assertEqual(reason, "movement_conflict")

    def test_can_schedule_motion_rejects_head_on_enemy_swap(self):
        """בודק שתנועת החלפה עימותית בין אויבים באותו זמן נדחית."""
        board = Board([
            ["bP", "wP"],
            [EMPTY_CELL, EMPTY_CELL],
        ])
        arbiter = RealTimeArbiter(move_time=1)
        arbiter.start_motion(Position(0, 0), Position(0, 1), 0, "bP")

        can_schedule, reason = arbiter.can_schedule_motion(
            board, Position(0, 1), Position(0, 0), 0, "wP"
        )
        self.assertFalse(can_schedule)
        self.assertEqual(reason, "enemy_collision")

    def test_can_schedule_motion_rejects_friendly_airborne_destination(self):
        """בודק שלא ניתן לנחות על משבצת עם כלי ידיד באוויר."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            ["wP", EMPTY_CELL],
        ])
        arbiter = RealTimeArbiter(move_time=1)
        arbiter.start_jump(Position(1, 0), 0, "wP")

        can_schedule, reason = arbiter.can_schedule_motion(
            board, Position(0, 0), Position(1, 0), 1000, "wN"
        )
        self.assertFalse(can_schedule)
        self.assertEqual(reason, "friendly_piece")

    def test_can_schedule_jump_rejects_empty_source(self):
        """בודק שלא ניתן לבצע jump ממשבצת ריקה."""
        board = Board([[EMPTY_CELL, EMPTY_CELL], [EMPTY_CELL, EMPTY_CELL]])
        arbiter = RealTimeArbiter(move_time=1)

        can_jump, reason = arbiter.can_schedule_jump(
            board, Position(0, 0), 0, EMPTY_CELL
        )
        self.assertFalse(can_jump)
        self.assertEqual(reason, "empty_source")

    def test_can_schedule_jump_rejects_active_jump_on_same_cell(self):
        """בודק שלא ניתן לבצע jump שני על אותה משבצת."""
        board = Board([[EMPTY_CELL, EMPTY_CELL], ["wP", EMPTY_CELL]])
        arbiter = RealTimeArbiter(move_time=1)
        arbiter.start_jump(Position(1, 0), 0, "wP")

        can_jump, reason = arbiter.can_schedule_jump(
            board, Position(1, 0), 0, "wP"
        )
        self.assertFalse(can_jump)
        self.assertEqual(reason, "motion_in_progress")

    def test_advance_time_airborne_piece_captures_arriving_enemy(self):
        """בודק שכלי באוויר תופס אויב שמגיע לאותה משבצת."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            ["wP", EMPTY_CELL],
            ["bR", EMPTY_CELL],
        ])
        arbiter = RealTimeArbiter(move_time=1)
        arbiter.start_jump(Position(1, 0), 0, "wP")
        arbiter.start_motion(Position(2, 0), Position(1, 0), 0, "bR")

        executed = arbiter.advance_time(board, 1)

        self.assertEqual(board.get_cell(1, 0), "wP")
        self.assertEqual(board.get_cell(2, 0), EMPTY_CELL)
        self.assertEqual(executed[0][1], "bR")


if __name__ == "__main__":
    unittest.main()
