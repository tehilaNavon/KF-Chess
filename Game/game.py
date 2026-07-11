from constants import COMMAND_PRINT_BOARD, COMMAND_WAIT, COMMAND_CLICK
from Game.controller import Controller
from Game.game_engine import GameEngine


class Game:

    def __init__(self, board):
        self.board = board
        self.game_engine = GameEngine(board, move_time=1000)
        self.controller = Controller(board, self.game_engine)

    def apply_command(self, command):
        if command == COMMAND_PRINT_BOARD:
            self.print_board()
            return

        tokens = command.split()
        if not tokens:
            return

        verb = tokens[0]
        if verb == COMMAND_WAIT and len(tokens) == 2:
            self.wait(int(tokens[1]))
            return

        if verb == COMMAND_CLICK and len(tokens) == 3:
            self.click(int(tokens[1]), int(tokens[2]))

    def click(self, x, y):
        result = self.controller.handle_click(x, y)
        if result is not None:
            pass

    def wait(self, ms):
        self.game_engine.advance_time(ms)

    def print_board(self):
        self.game_engine.realtime_arbiter.advance_time(self.board, self.game_engine.current_time)
        self.board.print_board()

