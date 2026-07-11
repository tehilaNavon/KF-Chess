from constants import MOVE_TIME, EMPTY_CELL
from models import Position


class Motion:
    def __init__(self, source, destination, arrival_time, piece_code):
        self.source = source
        self.destination = destination
        self.arrival_time = arrival_time
        self.piece_code = piece_code
        self.piece_color = piece_code[0] if piece_code != EMPTY_CELL else None


class RealTimeArbiter:
    def __init__(self, move_time=MOVE_TIME):
        self.move_time = move_time
        self.active_motions = []

    def has_active_motion(self):
        return bool(self.active_motions)

    def compute_arrival_time(self, source, destination, current_time):
        distance = max(abs(destination.row - source.row), abs(destination.col - source.col))
        return current_time + distance * self.move_time

    def is_source_in_motion(self, source):
        return any(motion.source == source for motion in self.active_motions)

    def will_destination_be_vacated(self, destination, arrival_time):
        for motion in self.active_motions:
            if motion.source == destination and motion.arrival_time <= arrival_time:
                return True
        return False

    def can_schedule_motion(self, board, source, destination, current_time, piece_code):
        arrival_time = self.compute_arrival_time(source, destination, current_time)

        if self.is_source_in_motion(source):
            return False, "motion_in_progress"

        destination_cell = board.get_cell(destination.row, destination.col)
        if destination_cell != EMPTY_CELL and destination_cell[0] == piece_code[0]:
            if not self.will_destination_be_vacated(destination, arrival_time):
                return False, "friendly_piece"

        for motion in self.active_motions:
            if motion.destination == destination:
                if motion.arrival_time == arrival_time:
                    if motion.piece_color != piece_code[0]:
                        return False, "enemy_collision"
                    return False, "movement_conflict"
                if motion.arrival_time < arrival_time:
                    return False, "movement_conflict"

            if motion.source == destination and motion.destination == source and motion.arrival_time == arrival_time:
                return False, "enemy_collision"

        return True, "ok"

    def start_motion(self, source, destination, current_time, piece_code):
        arrival_time = self.compute_arrival_time(source, destination, current_time)
        motion = Motion(source, destination, arrival_time, piece_code)
        self.active_motions.append(motion)
        return motion

    def advance_time(self, board, current_time):
        still_pending = []
        captured_pieces = []
        for motion in self.active_motions:
            if current_time >= motion.arrival_time:
                captured = board.move_piece(
                    motion.source.row,
                    motion.source.col,
                    motion.destination.row,
                    motion.destination.col,
                )
                if captured != EMPTY_CELL:
                    captured_pieces.append(captured)
            else:
                still_pending.append(motion)
        self.active_motions = still_pending
        return captured_pieces
