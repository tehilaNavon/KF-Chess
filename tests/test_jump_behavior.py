import unittest

from board import Board
from constants import EMPTY_CELL
from Game.game_engine import GameEngine
from models import Position


class TestJumpBehavior(unittest.TestCase):
    def test_jump_captures_arriving_enemy(self):
        board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            ["wP", EMPTY_CELL],
            ["bR", EMPTY_CELL],
        ])
        engine = GameEngine(board, move_time=1)

        # white pawn jumps at (1,0)
        res = engine.request_jump(Position(1, 0))
        self.assertTrue(res.is_valid)

        # enemy knight moves to (1,0) arriving at time 1
        res2 = engine.request_move(Position(2, 0), Position(1, 0))
        self.assertTrue(res2.is_valid)

        engine.advance_time(1)

        # arriving enemy removed, airborne piece still at (1,0)
        self.assertEqual(board.get_cell(2, 1), EMPTY_CELL)
        self.assertEqual(board.get_cell(1, 0), "wP")

    def test_jump_lands_if_no_enemy_arrives(self):
        board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            ["wP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL],
        ])
        engine = GameEngine(board, move_time=1)

        res = engine.request_jump(Position(1, 0))
        self.assertTrue(res.is_valid)

        engine.advance_time(1000)

        # pawn lands (remains in same cell logically)
        self.assertEqual(board.get_cell(1, 0), "wP")

    def test_moving_piece_cannot_jump(self):
        board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            ["wP", EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL],
        ])
        engine = GameEngine(board, move_time=100)

        # schedule move
        engine.request_move(Position(1, 0), Position(0, 0))
        # try to jump the same piece
        res = engine.request_jump(Position(1, 0))
        self.assertFalse(res.is_valid)
        self.assertEqual(res.reason, "motion_in_progress")

    def test_captured_piece_cannot_jump(self):
        board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            ["wP", EMPTY_CELL],
            ["bR", EMPTY_CELL],
        ])
        engine = GameEngine(board, move_time=1)

        # bR captures wP by moving to (1,0)
        engine.request_move(Position(2, 0), Position(1, 0))
        engine.advance_time(1)

        # captured piece (wP) is removed from board
        flat = [c for row in board.grid for c in row]
        self.assertNotIn("wP", flat)
