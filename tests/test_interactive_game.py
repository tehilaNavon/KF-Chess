import unittest

from board import Board
from constants import PIECE_STATE_LONG_REST
from Display.animation.frame_highlight import build_frame_highlight, with_selected_position
from Display.app.interactive_game import InteractiveGameApp, MouseInputHandler
from Display.starting_board import create_standard_starting_grid
from Game.game import Game
from models import Position


class TestInteractiveGame(unittest.TestCase):
    def test_mouse_input_left_click_selects_piece(self):
        board = Board(create_standard_starting_grid())
        game = Game(board)
        mouse_input = MouseInputHandler(game)

        result = mouse_input.handle_left_button(450, 650)

        self.assertIsNone(result)
        self.assertEqual(game.controller.selected, Position(6, 4))

    def test_mouse_input_right_click_requests_jump(self):
        board = Board([["wP", "."], [".", "."]])
        game = Game(board)
        mouse_input = MouseInputHandler(game)

        result = mouse_input.handle_right_button(50, 50)

        self.assertTrue(result.is_valid)

    def test_frame_highlight_marks_selected_cell(self):
        board = Board(create_standard_starting_grid())
        app = InteractiveGameApp(board)
        app._game.controller.selected = Position(6, 4)

        frame_highlight = build_frame_highlight(
            app._game.board,
            app._game.game_engine.realtime_arbiter,
            app._game.game_engine.current_time,
        )
        frame_highlight = with_selected_position(
            frame_highlight,
            app._game.controller.selected,
        )

        self.assertIn((6, 4), frame_highlight.selected_cells)

    def test_interactive_app_advances_time_on_tick(self):
        app = InteractiveGameApp()
        start_time = app._game.game_engine.current_time
        app._tick()
        self.assertEqual(app._game.game_engine.current_time, start_time + 16)


if __name__ == "__main__":
    unittest.main()
