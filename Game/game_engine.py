from constants import EMPTY_CELL
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

    def validate_move(self, source, destination):
        if self.is_game_over:
            return MoveResult(False, "game_over")

        if self.realtime_arbiter.is_source_in_motion(source):
            return MoveResult(False, "motion_in_progress")

        piece_code = self.board.get_cell(source.row, source.col)

        is_valid, reason = self.rule_engine.validate_move(
            self.board,
            source,
            destination,
            piece_code[0],
        )
        if not is_valid:
            return MoveResult(False, reason)

        can_schedule, reason = self.realtime_arbiter.can_schedule_motion(
            self.board,
            source,
            destination,
            self.current_time,
            piece_code,
        )
        if not can_schedule:
            return MoveResult(False, reason)

        return MoveResult(True, "ok")

    def execute_move(self, source, destination):
        piece_code = self.board.get_cell(source.row, source.col)
        self.realtime_arbiter.start_motion(source, destination, self.current_time, piece_code)

    def request_move(self, source, destination):
        result = self.validate_move(source, destination)
        if result.is_valid:
            self.execute_move(source, destination)
        return result

    def validate_jump(self, source):
        if self.is_game_over:
            return MoveResult(False, "game_over")

        piece_code = self.board.get_cell(source.row, source.col)
        if piece_code == EMPTY_CELL:
            return MoveResult(False, "empty_source")

        if self.realtime_arbiter.is_source_in_motion(source):
            return MoveResult(False, "motion_in_progress")

        can_jump, reason = self.realtime_arbiter.can_schedule_jump(
            self.board, source, self.current_time, piece_code
        )
        if not can_jump:
            return MoveResult(False, reason)

        return MoveResult(True, "ok")

    def execute_jump(self, source):
        piece_code = self.board.get_cell(source.row, source.col)
        self.realtime_arbiter.start_jump(source, self.current_time, piece_code)

    def request_jump(self, source):
        result = self.validate_jump(source)
        if result.is_valid:
            self.execute_jump(source)
        return result

    def sync_board_state(self):
        self.realtime_arbiter.advance_time(self.board, self.current_time)

    def tick(self, ms):
        self.current_time += ms

    def apply_promotion(self, motion):
        if motion.piece_code[1] == "P" and self.board.is_promotion_square(
            motion.destination.row, motion.piece_code[0]
        ):
            promotion_token = f"{motion.piece_code[0]}Q"
            self.board.set_cell(motion.destination.row, motion.destination.col, promotion_token)

    def check_game_over(self, captured):
        if captured in ("wK", "bK"):
            self.is_game_over = True

    def process_executed_motions(self, executed):
        for motion, captured in executed:
            self.apply_promotion(motion)
            self.check_game_over(captured)

    def advance_time(self, ms):
        self.tick(ms)
        executed = self.realtime_arbiter.advance_time(self.board, self.current_time)
        self.process_executed_motions(executed)
        return self.current_time
