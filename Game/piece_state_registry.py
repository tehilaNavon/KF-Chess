from constants import PIECE_STATE_IDLE, PIECE_STATE_LONG_REST, PIECE_STATE_SHORT_REST


class PieceRestRecord:
    def __init__(self, rest_state_name, rest_until_time):
        self.rest_state_name = rest_state_name
        self.rest_until_time = rest_until_time


class PieceRestRegistry:
    def __init__(self):
        self._rest_by_position = {}

    def _position_key(self, position):
        return (position.row, position.col)

    def is_position_resting(self, position, current_time):
        record = self._rest_by_position.get(self._position_key(position))
        if record is None:
            return False
        return current_time < record.rest_until_time

    def get_rest_state_name(self, position, current_time):
        record = self._rest_by_position.get(self._position_key(position))
        if record is None or current_time >= record.rest_until_time:
            return PIECE_STATE_IDLE
        return record.rest_state_name

    def get_rest_elapsed_ms(self, position, current_time, rest_duration_ms):
        record = self._rest_by_position.get(self._position_key(position))
        if record is None or current_time >= record.rest_until_time:
            return 0
        rest_start_time = record.rest_until_time - rest_duration_ms
        return max(0, current_time - rest_start_time)

    def schedule_rest(self, position, rest_state_name, current_time, duration_ms):
        if duration_ms <= 0:
            self.clear_rest(position)
            return
        rest_until_time = current_time + duration_ms
        record = PieceRestRecord(rest_state_name, rest_until_time)
        self._rest_by_position[self._position_key(position)] = record

    def clear_rest(self, position):
        self._rest_by_position.pop(self._position_key(position), None)

    def expire_finished_rests(self, current_time):
        expired_positions = []
        for position_key, record in self._rest_by_position.items():
            if current_time >= record.rest_until_time:
                expired_positions.append(position_key)
        for position_key in expired_positions:
            del self._rest_by_position[position_key]
