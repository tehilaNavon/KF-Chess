from constants import COMMAND_PRINT_BOARD, COMMAND_WAIT, COMMAND_CLICK, COMMAND_JUMP
from Game.controller import Controller
from Game.game_engine import GameEngine, MoveResult


class Game:

    def __init__(self, board):
        self.board = board
        self.game_engine = GameEngine(board, move_time=1000)
        self.controller = Controller(board, self.game_engine)

    def _report_move_result(self, result):
        if isinstance(result, MoveResult) and not result.is_valid:
            print(f"ERROR {result.reason}")

    def apply_command(self, command):
        if command == COMMAND_PRINT_BOARD:
            self.print_board()
            return

        tokens = command.split()
        if not tokens:
            return

        verb = tokens[0]
        handlers = {
            COMMAND_WAIT: (self.wait, 1),
            COMMAND_CLICK: (self.click, 2),
            COMMAND_JUMP: (self.jump, 2),
        }

        if verb in handlers:
            handler, expected_args = handlers[verb]
            if len(tokens) - 1 == expected_args:
                try:
                    args = [int(token) for token in tokens[1:]]
                except ValueError:
                    print("ERROR INVALID_ARGUMENT")
                    return
                result = handler(*args)
                self._report_move_result(result)
            return

    def click(self, x, y):
        return self.controller.handle_click(x, y)

    def jump(self, x, y):
        return self.controller.handle_jump(x, y)

    def wait(self, ms):
        self.game_engine.advance_time(ms)

    def print_board(self):
        self.game_engine.sync_board_state()
        self.board.print_board()

