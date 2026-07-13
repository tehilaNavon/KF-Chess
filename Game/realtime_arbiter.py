from constants import MOVE_TIME, EMPTY_CELL
from models import Position


# Jump duration is fixed at 1000 ms per spec
JUMP_DURATION = 1000


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
        self.active_jumps = []

    def has_active_motion(self):
        return bool(self.active_motions) or bool(self.active_jumps)

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

    def is_cell_airborne_at(self, destination, at_time):
        for jump in self.active_jumps:
            if (
                jump['cell'].row == destination.row
                and jump['cell'].col == destination.col
                and jump['start_time'] <= at_time <= jump['end_time']
            ):
                return True, jump
        return False, None

    def can_schedule_motion(self, board, source, destination, current_time, piece_code):
        arrival_time = self.compute_arrival_time(source, destination, current_time)

        if self.is_source_in_motion(source):
            return False, "motion_in_progress"

        destination_cell = board.get_cell(destination.row, destination.col)
        # If destination currently has a friendly piece, disallow unless it will vacate.
        if destination_cell != EMPTY_CELL and destination_cell[0] == piece_code[0]:
            if not self.will_destination_be_vacated(destination, arrival_time):
                return False, "friendly_piece"

        # If destination is occupied by a friendly airborne piece during arrival, block.
        airborne, jump = self.is_cell_airborne_at(destination, arrival_time)
        if airborne and jump and jump['piece_code'][0] == piece_code[0]:
            return False, "friendly_piece"

        for motion in self.active_motions:
            if motion.destination == destination and motion.piece_color == piece_code[0]:
                if motion.arrival_time == arrival_time:
                    return False, "movement_conflict"
                if motion.arrival_time < arrival_time:
                    return False, "movement_conflict"

            if motion.source == destination and motion.destination == source and motion.arrival_time == arrival_time:
                if motion.piece_color != piece_code[0]:
                    return False, "enemy_collision"

        return True, "ok"

    def can_schedule_jump(self, board, source, current_time, piece_code):
        # Can't jump if source is moving or empty
        if self.is_source_in_motion(source):
            return False, "motion_in_progress"
        if piece_code == EMPTY_CELL:
            return False, "empty_source"
        # Can't jump if source already has a jump active
        for jump in self.active_jumps:
            if jump['cell'] == source:
                return False, "motion_in_progress"
        return True, "ok"

    def start_motion(self, source, destination, current_time, piece_code):
        arrival_time = self.compute_arrival_time(source, destination, current_time)
        motion = Motion(source, destination, arrival_time, piece_code)
        self.active_motions.append(motion)
        return motion

    def start_jump(self, source, current_time, piece_code):
        start_time = current_time
        end_time = start_time + JUMP_DURATION
        jump = {
            'cell': source,
            'start_time': start_time,
            'end_time': end_time,
            'piece_code': piece_code,
            'piece_color': piece_code[0] if piece_code != EMPTY_CELL else None,
        }
        self.active_jumps.append(jump)
        return jump

    def advance_time(self, board, current_time):
        still_pending = []
        executed = []

        for motion in self.active_motions:
            if current_time >= motion.arrival_time:
                airborne, jump = self.is_cell_airborne_at(motion.destination, current_time)
                if airborne and jump and jump['piece_color'] != motion.piece_color:
                    captured = motion.piece_code
                    board.set_cell(motion.source.row, motion.source.col, EMPTY_CELL)
                    executed.append((motion, captured))
                else:
                    captured = board.move_piece(
                        motion.source.row,
                        motion.source.col,
                        motion.destination.row,
                        motion.destination.col,
                    )
                    executed.append((motion, captured))
            else:
                still_pending.append(motion)

        self.active_motions = still_pending

        # Remove expired jumps
        still_jumps = []
        for jump in self.active_jumps:
            if current_time < jump['end_time']:
                still_jumps.append(jump)
        self.active_jumps = still_jumps


        return executed
