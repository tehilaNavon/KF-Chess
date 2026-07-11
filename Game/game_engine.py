from constants import EMPTY_CELL
from models import Position
from Game.realtime_arbiter import RealTimeArbiter
from Rules.rules import RuleEngine


class MoveResult:
    def __init__(self, is_valid, reason="ok"):
        self.is_valid = is_valid
        self.reason = reason


class GameEngine:
    def __init__(self, board, move_time=0):
        self.board = board
        self.is_game_over = False
        self.current_time = 0
        self.rule_engine = RuleEngine()
        self.realtime_arbiter = RealTimeArbiter(move_time=move_time or 1000)

    def request_move(self, source, destination):
        if self.is_game_over:
            return MoveResult(False, "game_over")

        if self.realtime_arbiter.has_active_motion():
            return MoveResult(False, "motion_in_progress")

        if source == destination:
            return MoveResult(False, "same_square")

        is_valid, reason = self.rule_engine.validate_move(self.board, source, destination)
        if not is_valid:
            return MoveResult(False, reason)

        self.realtime_arbiter.start_motion(source, destination, self.current_time)
        return MoveResult(True, "ok")

    def advance_time(self, ms):
        self.current_time += ms
        self.realtime_arbiter.advance_time(self.board, self.current_time)
        return self.current_time
