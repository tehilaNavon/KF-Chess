import unittest

from board import Board
from constants import ASSETS_PIECES_ROOT, EMPTY_CELL, PIECE_STATE_LONG_REST, PIECE_STATE_SHORT_REST
from Game.motion_physics import compute_travel_duration_ms
from Game.piece_config import PieceConfigRegistry
from Game.realtime_arbiter import RealTimeArbiter
from models import Position


class TestMotionPhysics(unittest.TestCase):
    def test_compute_travel_duration_ms_for_one_cell(self):
        duration_ms = compute_travel_duration_ms(1, speed_m_per_sec=1.5)
        self.assertEqual(duration_ms, 666)

    def test_compute_travel_duration_ms_for_zero_distance(self):
        duration_ms = compute_travel_duration_ms(0, speed_m_per_sec=1.5)
        self.assertEqual(duration_ms, 0)


class TestPieceConfigRegistry(unittest.TestCase):
    def test_uniform_move_time_sets_travel_speed(self):
        registry = PieceConfigRegistry(uniform_move_time_ms=5)
        speed_m_per_sec = registry.get_travel_speed_m_per_sec("wP")
        self.assertEqual(speed_m_per_sec, 200)

    def test_uniform_move_time_disables_rest_duration(self):
        registry = PieceConfigRegistry(uniform_move_time_ms=5)
        rest_duration_ms = registry.get_rest_duration_ms("wP", PIECE_STATE_LONG_REST)
        self.assertEqual(rest_duration_ms, 0)

    def test_default_config_uses_ctd_speed(self):
        registry = PieceConfigRegistry()
        speed_m_per_sec = registry.get_travel_speed_m_per_sec("wP")
        self.assertEqual(speed_m_per_sec, 1.5)

    def test_assets_folder_loads_config_from_disk(self):
        registry = PieceConfigRegistry(assets_root=ASSETS_PIECES_ROOT)
        move_config = registry.get_state_config("wP", "move")
        self.assertEqual(move_config.speed_m_per_sec, 1.5)
        self.assertEqual(move_config.frame_count, 5)


class TestPieceRestBehavior(unittest.TestCase):
    def test_piece_enters_long_rest_after_move_arrives(self):
        board = Board([[EMPTY_CELL, EMPTY_CELL], ["wP", EMPTY_CELL]])
        arbiter = RealTimeArbiter()
        arbiter.start_motion(Position(1, 0), Position(0, 0), 0, "wP")

        arbiter.advance_time(board, 700)

        self.assertTrue(arbiter.is_source_resting(Position(0, 0), 700))
        self.assertEqual(
            arbiter.piece_rest_registry.get_rest_state_name(Position(0, 0), 700),
            PIECE_STATE_LONG_REST,
        )

    def test_piece_cannot_move_during_long_rest(self):
        board = Board([[EMPTY_CELL, EMPTY_CELL], ["wP", EMPTY_CELL]])
        arbiter = RealTimeArbiter()
        arbiter.start_motion(Position(1, 0), Position(0, 0), 0, "wP")
        arbiter.advance_time(board, 700)

        can_schedule, reason = arbiter.can_schedule_motion(
            board, Position(0, 0), Position(0, 1), 700, "wP"
        )
        self.assertFalse(can_schedule)
        self.assertEqual(reason, "motion_in_progress")

    def test_piece_can_move_after_long_rest_expires(self):
        board = Board([[EMPTY_CELL, EMPTY_CELL], ["wP", EMPTY_CELL]])
        arbiter = RealTimeArbiter()
        arbiter.start_motion(Position(1, 0), Position(0, 0), 0, "wP")
        arbiter.advance_time(board, 1500)

        can_schedule, reason = arbiter.can_schedule_motion(
            board, Position(0, 0), Position(0, 1), 1500, "wP"
        )
        self.assertTrue(can_schedule)
        self.assertEqual(reason, "ok")

    def test_piece_enters_short_rest_after_jump(self):
        board = Board([[EMPTY_CELL, EMPTY_CELL], ["wP", EMPTY_CELL]])
        arbiter = RealTimeArbiter()
        arbiter.start_jump(Position(1, 0), 0, "wP")

        arbiter.advance_time(board, 625)

        self.assertTrue(arbiter.is_source_resting(Position(1, 0), 625))
        self.assertEqual(
            arbiter.piece_rest_registry.get_rest_state_name(Position(1, 0), 625),
            PIECE_STATE_SHORT_REST,
        )


if __name__ == "__main__":
    unittest.main()
