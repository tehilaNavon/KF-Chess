import tempfile
import unittest
from pathlib import Path

from board import Board
from Display.rendering.board_renderer import BoardRenderer
from Display.starting_board import create_standard_starting_board, create_standard_starting_grid


class TestStaticDisplay(unittest.TestCase):
    def test_create_standard_starting_board_returns_board(self):
        board = create_standard_starting_board()
        self.assertEqual(board.grid, create_standard_starting_grid())

    def test_render_starting_board_returns_image(self):
        canvas = BoardRenderer().render(create_standard_starting_board())
        self.assertIsNotNone(canvas.img)
        self.assertEqual(canvas.img.shape[0], 800)
        self.assertEqual(canvas.img.shape[1], 800)

    def test_render_saves_png_file(self):
        canvas = BoardRenderer().render(create_standard_starting_board())
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "board.png"
            canvas.save(output_path)
            self.assertTrue(output_path.exists())

    def test_render_custom_board(self):
        board = Board([
            [".", "wK"],
            ["bK", "."],
        ])
        canvas = BoardRenderer().render(board)
        self.assertEqual(canvas.img.shape[0], 200)
        self.assertEqual(canvas.img.shape[1], 200)


if __name__ == "__main__":
    unittest.main()
