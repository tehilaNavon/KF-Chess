from constants import MOVE_TIME
from models import Position


class Motion:
    def __init__(self, source, destination, arrival_time):
        self.source = source
        self.destination = destination
        self.arrival_time = arrival_time


class RealTimeArbiter:
    def __init__(self, move_time=MOVE_TIME):
        self.move_time = move_time
        self.active_motions = []

    def has_active_motion(self):
        return bool(self.active_motions)

    def start_motion(self, source, destination, current_time):
        distance = max(abs(destination.row - source.row), abs(destination.col - source.col))
        arrival_time = current_time + distance * self.move_time
        motion = Motion(source, destination, arrival_time)
        self.active_motions.append(motion)
        return motion

    def advance_time(self, board, current_time):
        still_pending = []
        for motion in self.active_motions:
            if current_time >= motion.arrival_time:
                board.move_piece(motion.source.row, motion.source.col, motion.destination.row, motion.destination.col)
            else:
                still_pending.append(motion)
        self.active_motions = still_pending
        return self.active_motions
