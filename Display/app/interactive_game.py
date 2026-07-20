import cv2

from board import Board
from constants import INTERACTIVE_FRAME_MS, format_error
from Display.animation.frame_highlight import build_frame_highlight, with_selected_position
from Display.rendering.animated_board_renderer import AnimatedBoardRenderer
from Display.starting_board import create_standard_starting_board
from Game.game import Game


class MouseInputHandler:
    def __init__(self, game):
        self._game = game

    def handle_left_button(self, pixel_x, pixel_y):
        return self._game.controller.handle_click(pixel_x, pixel_y)

    def handle_right_button(self, pixel_x, pixel_y):
        self._game.controller.selected = None
        return self._game.controller.handle_jump(pixel_x, pixel_y)


class InteractiveGameApp:
    WINDOW_NAME = "Chess Game"
    ERROR_DISPLAY_MS = 2000

    def __init__(self, board=None):
        self._game = Game(board or create_standard_starting_board())
        self._mouse_input = MouseInputHandler(self._game)
        self._renderer = AnimatedBoardRenderer()
        self._renderer.set_piece_config_registry(
            self._game.game_engine.realtime_arbiter.piece_config_registry
        )
        self._last_error_message = None
        self._error_visible_until = 0
        self._is_running = False

    def run(self):
        self._print_controls()
        cv2.namedWindow(self.WINDOW_NAME)
        cv2.setMouseCallback(self.WINDOW_NAME, self._on_mouse_event)
        self._is_running = True
        try:
            while self._is_running:
                self._tick()
                key = cv2.waitKey(INTERACTIVE_FRAME_MS) & 0xFF
                if key in (ord("q"), 27):
                    break
        finally:
            cv2.destroyAllWindows()
            self._is_running = False

    def _tick(self):
        self._game.game_engine.advance_time(INTERACTIVE_FRAME_MS)
        self._render_frame()

    def _on_mouse_event(self, event, pixel_x, pixel_y, _flags, _param):
        if self._game.game_engine.is_game_over:
            return
        if event == cv2.EVENT_LBUTTONDOWN:
            result = self._mouse_input.handle_left_button(pixel_x, pixel_y)
            self._store_action_result(result)
            return
        if event == cv2.EVENT_RBUTTONDOWN:
            result = self._mouse_input.handle_right_button(pixel_x, pixel_y)
            self._store_action_result(result)

    def _store_action_result(self, result):
        if result is None:
            return
        if not result.is_valid:
            self._last_error_message = format_error(result.reason)
            self._error_visible_until = (
                self._game.game_engine.current_time + self.ERROR_DISPLAY_MS
            )

    def _render_frame(self):
        frame_highlight = build_frame_highlight(
            self._game.board,
            self._game.game_engine.realtime_arbiter,
            self._game.game_engine.current_time,
        )
        frame_highlight = with_selected_position(
            frame_highlight,
            self._game.controller.selected,
        )
        canvas = self._renderer.render(
            self._game.board,
            self._game.game_engine.realtime_arbiter,
            self._game.game_engine.current_time,
            frame_highlight=frame_highlight,
        )
        display_image = self._to_display_image(canvas.img)
        self._draw_status_bar(display_image)
        cv2.imshow(self.WINDOW_NAME, display_image)

    def _draw_status_bar(self, display_image):
        bar_height = 40
        cv2.rectangle(display_image, (0, 0), (display_image.shape[1], bar_height), (30, 30, 30), -1)
        status_text = self._build_status_text()
        cv2.putText(
            display_image,
            status_text,
            (12, 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (240, 240, 240),
            1,
            cv2.LINE_AA,
        )

    def _build_status_text(self):
        if self._game.game_engine.is_game_over:
            return "GAME OVER - press Q to quit"
        if self._is_error_visible():
            return self._last_error_message
        if self._game.controller.selected is not None:
            return "Piece selected - click destination (right click = jump)"
        return "Left click: select/move | Right click: jump | Q: quit"

    def _is_error_visible(self):
        if self._last_error_message is None:
            return False
        return self._game.game_engine.current_time < self._error_visible_until

    def _to_display_image(self, image):
        if image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        return image

    def _print_controls(self):
        print("Chess Game started.")
        print("Left click: select piece, then click destination to move.")
        print("Right click: jump on clicked piece.")
        print("Press Q or Esc to quit.")


def run_interactive_game(board=None):
    InteractiveGameApp(board=board).run()


if __name__ == "__main__":
    run_interactive_game()
