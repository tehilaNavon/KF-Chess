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

        if source == destination:
            return MoveResult(False, "same_square")

        piece_code = self.board.get_cell(source.row, source.col)
        if piece_code == EMPTY_CELL:
            return MoveResult(False, "empty_source")

        if self.realtime_arbiter.is_source_in_motion(source):
            return MoveResult(False, "motion_in_progress")

        arrival_time = self.realtime_arbiter.compute_arrival_time(source, destination, self.current_time)
        color = piece_code[0]

        is_valid, reason = self.rule_engine.validate_move(
            self.board,
            source,
            destination,
            color,
            arrival_time=arrival_time,
            pending_motions=self.realtime_arbiter.active_motions,
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

        self.realtime_arbiter.start_motion(source, destination, self.current_time, piece_code)
        return MoveResult(True, "ok")

    def request_jump(self, source):
        """Request a jump (airborne) for the piece at `source`.

        Returns MoveResult like request_move.
        """
        if self.is_game_over:
            return MoveResult(False, "game_over")

        piece_code = self.board.get_cell(source.row, source.col)
        if piece_code == EMPTY_CELL:
            return MoveResult(False, "empty_source")

        # captured pieces or moving pieces cannot jump
        if self.realtime_arbiter.is_source_in_motion(source):
            return MoveResult(False, "motion_in_progress")

        can_jump, reason = self.realtime_arbiter.can_schedule_jump(self.board, source, self.current_time, piece_code)
        if not can_jump:
            return MoveResult(False, reason)

        self.realtime_arbiter.start_jump(source, self.current_time, piece_code)
        return MoveResult(True, "ok")

    def advance_time(self, ms):
        self.current_time += ms
        executed = self.realtime_arbiter.advance_time(self.board, self.current_time)
        for motion, captured in executed:
            if motion.piece_code[1] == "P" and self.board.is_promotion_square(
                motion.destination.row, motion.piece_code[0]
            ):
                promotion_token = f"{motion.piece_code[0]}Q"
                self.board.set_cell(motion.destination.row, motion.destination.col, promotion_token)
            if captured in ("wK", "bK"):
                self.is_game_over = True
        return self.current_time
