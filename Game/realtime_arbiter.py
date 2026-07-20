from constants import (
    EMPTY_CELL,
    ERROR_EMPTY_SOURCE,
    ERROR_ENEMY_COLLISION,
    ERROR_FRIENDLY_PIECE,
    ERROR_MOTION_IN_PROGRESS,
    ERROR_MOVEMENT_CONFLICT,
    ERROR_OK,
    PIECE_STATE_LONG_REST,
    PIECE_STATE_SHORT_REST,
)
from Game.motion_physics import compute_chebyshev_distance, compute_travel_duration_ms
from Game.piece_config import PieceConfigRegistry
from Game.piece_state_registry import PieceRestRegistry


class Motion:
    def __init__(self, source, destination, arrival_time, piece_code):
        self.source = source
        self.destination = destination
        self.arrival_time = arrival_time
        self.piece_code = piece_code
        self.piece_color = piece_code[0] if piece_code != EMPTY_CELL else None


class RealTimeArbiter:
    def __init__(self, move_time=None, piece_config_registry=None, assets_root=None):
        if piece_config_registry is not None:
            self.piece_config_registry = piece_config_registry
        else:
            self.piece_config_registry = PieceConfigRegistry(
                assets_root=assets_root,
                uniform_move_time_ms=move_time,
            )
        self.active_motions = []
        self.active_jumps = []
        self.piece_rest_registry = PieceRestRegistry()

    def has_active_motion(self):
        return bool(self.active_motions) or bool(self.active_jumps)

    def compute_arrival_time(self, source, destination, current_time, piece_code):
        distance_cells = compute_chebyshev_distance(source, destination)
        speed_m_per_sec = self.piece_config_registry.get_travel_speed_m_per_sec(piece_code)
        travel_duration_ms = compute_travel_duration_ms(distance_cells, speed_m_per_sec)
        return current_time + travel_duration_ms

    def is_source_in_motion(self, source):
        return any(motion.source == source for motion in self.active_motions)

    def is_source_resting(self, source, current_time):
        return self.piece_rest_registry.is_position_resting(source, current_time)

    def is_source_busy(self, source, current_time):
        if self.is_source_in_motion(source):
            return True
        if self.is_source_resting(source, current_time):
            return True
        return self._is_source_jumping(source)

    def will_destination_be_vacated(self, destination, arrival_time):
        for motion in self.active_motions:
            if motion.source == destination and motion.arrival_time <= arrival_time:
                return True
        return False

    def is_cell_airborne_at(self, destination, at_time):
        for jump in self.active_jumps:
            if (
                jump["cell"].row == destination.row
                and jump["cell"].col == destination.col
                and jump["start_time"] <= at_time <= jump["end_time"]
            ):
                return True, jump
        return False, None

    def can_schedule_motion(self, board, source, destination, current_time, piece_code):
        if self.is_source_busy(source, current_time):
            return False, ERROR_MOTION_IN_PROGRESS

        arrival_time = self.compute_arrival_time(source, destination, current_time, piece_code)

        destination_cell = board.get_cell(destination.row, destination.col)
        if destination_cell != EMPTY_CELL and destination_cell[0] == piece_code[0]:
            if not self.will_destination_be_vacated(destination, arrival_time):
                return False, ERROR_FRIENDLY_PIECE

        airborne, jump = self.is_cell_airborne_at(destination, arrival_time)
        if airborne and jump and jump["piece_code"][0] == piece_code[0]:
            return False, ERROR_FRIENDLY_PIECE

        for motion in self.active_motions:
            if motion.destination == destination and motion.piece_color == piece_code[0]:
                if motion.arrival_time == arrival_time:
                    return False, ERROR_MOVEMENT_CONFLICT
                if motion.arrival_time < arrival_time:
                    return False, ERROR_MOVEMENT_CONFLICT

            if motion.source == destination and motion.destination == source and motion.arrival_time == arrival_time:
                if motion.piece_color != piece_code[0]:
                    return False, ERROR_ENEMY_COLLISION

        return True, ERROR_OK

    def can_schedule_jump(self, board, source, current_time, piece_code):
        if self.is_source_busy(source, current_time):
            return False, ERROR_MOTION_IN_PROGRESS
        if piece_code == EMPTY_CELL:
            return False, ERROR_EMPTY_SOURCE
        return True, ERROR_OK

    def start_motion(self, source, destination, current_time, piece_code):
        arrival_time = self.compute_arrival_time(source, destination, current_time, piece_code)
        motion = Motion(source, destination, arrival_time, piece_code)
        self.active_motions.append(motion)
        self.piece_rest_registry.clear_rest(source)
        return motion

    def start_jump(self, source, current_time, piece_code):
        jump_duration_ms = self.piece_config_registry.get_jump_duration_ms(piece_code)
        start_time = current_time
        end_time = start_time + jump_duration_ms
        jump = {
            "cell": source,
            "start_time": start_time,
            "end_time": end_time,
            "piece_code": piece_code,
            "piece_color": piece_code[0] if piece_code != EMPTY_CELL else None,
        }
        self.active_jumps.append(jump)
        self.piece_rest_registry.clear_rest(source)
        return jump

    def partition_motions(self, current_time):
        arrived = []
        still_pending = []
        for motion in self.active_motions:
            if current_time >= motion.arrival_time:
                arrived.append(motion)
            else:
                still_pending.append(motion)
        return arrived, still_pending

    def resolve_arrival(self, board, motion, current_time):
        airborne, jump = self.is_cell_airborne_at(motion.destination, current_time)
        if airborne and jump and jump["piece_color"] != motion.piece_color:
            captured = motion.piece_code
            board.set_cell(motion.source.row, motion.source.col, EMPTY_CELL)
        else:
            captured = board.move_piece(
                motion.source.row,
                motion.source.col,
                motion.destination.row,
                motion.destination.col,
            )
        return captured

    def apply_arrival(self, board, motion, current_time):
        captured = self.resolve_arrival(board, motion, current_time)
        self._schedule_long_rest(motion.destination, motion.piece_code, motion.arrival_time)
        return motion, captured

    def partition_jumps(self, current_time):
        active_jumps = []
        finished_jumps = []
        for jump in self.active_jumps:
            if current_time >= jump["end_time"]:
                finished_jumps.append(jump)
            else:
                active_jumps.append(jump)
        return finished_jumps, active_jumps

    def apply_finished_jump(self, jump, current_time):
        self._schedule_short_rest(jump["cell"], jump["piece_code"], jump["end_time"])

    def advance_time(self, board, current_time):
        arrived, still_pending = self.partition_motions(current_time)
        executed = [self.apply_arrival(board, motion, current_time) for motion in arrived]
        self.active_motions = still_pending

        finished_jumps, active_jumps = self.partition_jumps(current_time)
        for jump in finished_jumps:
            self.apply_finished_jump(jump, current_time)
        self.active_jumps = active_jumps

        self.piece_rest_registry.expire_finished_rests(current_time)
        return executed

    def _is_source_jumping(self, source):
        return any(jump["cell"] == source for jump in self.active_jumps)

    def _schedule_long_rest(self, position, piece_code, current_time):
        rest_duration_ms = self.piece_config_registry.get_rest_duration_ms(
            piece_code,
            PIECE_STATE_LONG_REST,
        )
        self.piece_rest_registry.schedule_rest(
            position,
            PIECE_STATE_LONG_REST,
            current_time,
            rest_duration_ms,
        )

    def _schedule_short_rest(self, position, piece_code, current_time):
        rest_duration_ms = self.piece_config_registry.get_rest_duration_ms(
            piece_code,
            PIECE_STATE_SHORT_REST,
        )
        self.piece_rest_registry.schedule_rest(
            position,
            PIECE_STATE_SHORT_REST,
            current_time,
            rest_duration_ms,
        )
