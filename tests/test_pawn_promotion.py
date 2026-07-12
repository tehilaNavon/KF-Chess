import unittest

from board import Board
from constants import EMPTY_CELL
from models import Position
from Rules.rules import RuleEngine
from Game.game_engine import GameEngine


class TestPawnPromotion(unittest.TestCase):
    def setUp(self):
        self.engine = RuleEngine()

    def test_pawn_double_move_from_start_is_valid(self):
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])

        valid, reason = self.engine.validate_move(board, Position(2, 1), Position(0, 1))
        self.assertTrue(valid)
        self.assertEqual(reason, "ok")

    def test_pawn_double_move_requires_clear_path(self):
        board = Board([
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP", EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "bP", EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ])

        valid, reason = self.engine.validate_move(board, Position(1, 1), Position(3, 1))
        self.assertFalse(valid)
        self.assertEqual(reason, "illegal_move")

    def test_pawn_promotion_to_queen_via_game_engine(self):
        board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            ["wP", EMPTY_CELL],
        ])
        game_engine = GameEngine(board, move_time=1)
        result = game_engine.request_move(Position(1, 0), Position(0, 0))
        self.assertTrue(result.is_valid)
        game_engine.advance_time(1)
        self.assertEqual(board.get_cell(0, 0), "wQ")

    def test_black_pawn_promotion_to_queen_via_game_engine(self):
        board = Board([
            [EMPTY_CELL, "bP"],
            [EMPTY_CELL, EMPTY_CELL],
        ])
        game_engine = GameEngine(board, move_time=1)
        result = game_engine.request_move(Position(0, 1), Position(1, 1))
        self.assertTrue(result.is_valid)
        game_engine.advance_time(1)
        self.assertEqual(board.get_cell(1, 1), "bQ")
