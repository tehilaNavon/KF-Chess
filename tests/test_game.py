import io
import unittest
from contextlib import redirect_stdout

from board import Board
from constants import EMPTY_CELL
from Game.game import Game


class TestGame(unittest.TestCase):
    def test_apply_command_click_wait_and_print_board(self):
        """בודק שרצף click, wait ו-print board מדפיס לוח מעודכן."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP"],
        ])
        game = Game(board)

        game.apply_command("click 100 100")
        game.apply_command("click 100 0")
        game.apply_command("wait 1000")

        output = io.StringIO()
        with redirect_stdout(output):
            game.apply_command("print board")

        self.assertEqual(output.getvalue(), ". wQ\n. .\n")

    def test_apply_command_two_rook_moves_with_wait(self):
        """בודק שני מסעי צריח, wait ו-print board מדפיסים את מיקומי הכלים."""
        board = Board([
            ["wR", EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
            ["bR", EMPTY_CELL, EMPTY_CELL],
        ])
        game = Game(board)

        game.apply_command("click 50 50")
        game.apply_command("click 250 50")
        game.apply_command("click 50 250")
        game.apply_command("click 250 250")
        game.apply_command("wait 2000")

        output = io.StringIO()
        with redirect_stdout(output):
            game.apply_command("print board")

        self.assertEqual(
            output.getvalue(),
            ". . wR\n. . .\n. . bR\n",
        )

    def test_apply_command_jump_and_print_board(self):
        """בודק jump, wait ו-print board מדפיסים את הלוח."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            ["wP", EMPTY_CELL],
        ])
        game = Game(board)

        game.apply_command("jump 100 100")
        game.apply_command("wait 1000")

        output = io.StringIO()
        with redirect_stdout(output):
            game.apply_command("print board")

        self.assertEqual(output.getvalue(), ". .\nwP .\n")

    def test_apply_command_ignores_command_with_wrong_argument_count(self):
        """בודק שפקודה עם מספר ארגומנטים שגוי לא משנה את הלוח."""
        board = Board([
            [EMPTY_CELL, "wP"],
            [EMPTY_CELL, EMPTY_CELL],
        ])
        game = Game(board)

        game.apply_command("click 100")
        game.apply_command("wait 100 200")

        self.assertEqual(board.get_cell(0, 1), "wP")
        self.assertEqual(game.game_engine.current_time, 0)

    def test_apply_command_prints_illegal_move_error(self):
        """בודק שמהלך לא חוקי מדפיס הודעת שגיאה."""
        board = Board([
            [EMPTY_CELL, EMPTY_CELL],
            [EMPTY_CELL, "wP"],
        ])
        game = Game(board)

        output = io.StringIO()
        with redirect_stdout(output):
            game.apply_command("click 100 100")
            game.apply_command("click 0 100")

        self.assertEqual(output.getvalue(), "ERROR illegal_move\n")

    def test_apply_command_prints_invalid_argument_error(self):
        """בודק שארגומנט לא מספרי מדפיס הודעת שגיאה."""
        board = Board([
            [EMPTY_CELL, "wP"],
            [EMPTY_CELL, EMPTY_CELL],
        ])
        game = Game(board)

        output = io.StringIO()
        with redirect_stdout(output):
            game.apply_command("click abc def")

        self.assertEqual(output.getvalue(), "ERROR INVALID_ARGUMENT\n")


if __name__ == "__main__":
    unittest.main()
