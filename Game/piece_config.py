import json
import pathlib

from constants import (
    DEFAULT_IDLE_FRAME_COUNT,
    DEFAULT_JUMP_FRAME_COUNT,
    DEFAULT_LONG_REST_FRAME_COUNT,
    DEFAULT_MOVE_FRAME_COUNT,
    DEFAULT_SHORT_REST_FRAME_COUNT,
    METERS_PER_CELL,
    MS_PER_SECOND,
    PIECE_STATE_IDLE,
    PIECE_STATE_JUMP,
    PIECE_STATE_LONG_REST,
    PIECE_STATE_MOVE,
    PIECE_STATE_SHORT_REST,
)
from Game.motion_physics import compute_animation_duration_ms


class PieceStateConfig:
    def __init__(
        self,
        state_name,
        speed_m_per_sec,
        next_state_when_finished,
        frames_per_sec,
        is_loop,
        frame_count,
    ):
        self.state_name = state_name
        self.speed_m_per_sec = speed_m_per_sec
        self.next_state_when_finished = next_state_when_finished
        self.frames_per_sec = frames_per_sec
        self.is_loop = is_loop
        self.frame_count = frame_count

    def animation_duration_ms(self):
        return compute_animation_duration_ms(self.frame_count, self.frames_per_sec)


def piece_code_to_asset_folder(piece_code):
    color_code = piece_code[0].upper()
    piece_type = piece_code[1].upper()
    return f"{piece_type}{color_code}"


def _count_sprite_frames(sprites_dir):
    if not sprites_dir.is_dir():
        return 0
    return len(list(sprites_dir.glob("*.png")))


def _parse_config_file(config_path, state_name, frame_count):
    with config_path.open(encoding="utf-8") as config_file:
        raw_config = json.load(config_file)

    physics = raw_config["physics"]
    graphics = raw_config["graphics"]
    return PieceStateConfig(
        state_name=state_name,
        speed_m_per_sec=physics["speed_m_per_sec"],
        next_state_when_finished=physics["next_state_when_finished"],
        frames_per_sec=graphics["frames_per_sec"],
        is_loop=graphics["is_loop"],
        frame_count=frame_count,
    )


def _load_state_config_from_disk(piece_folder, state_name):
    state_dir = piece_folder / "states" / state_name
    config_path = state_dir / "config.json"
    frame_count = _count_sprite_frames(state_dir / "sprites")
    return _parse_config_file(config_path, state_name, frame_count)


def _default_state_config(state_name):
    defaults_by_state = {
        PIECE_STATE_IDLE: (0.0, PIECE_STATE_IDLE, 6, True, DEFAULT_IDLE_FRAME_COUNT),
        PIECE_STATE_MOVE: (1.5, PIECE_STATE_LONG_REST, 12, True, DEFAULT_MOVE_FRAME_COUNT),
        PIECE_STATE_JUMP: (3.0, PIECE_STATE_SHORT_REST, 8, False, DEFAULT_JUMP_FRAME_COUNT),
        PIECE_STATE_SHORT_REST: (0.0, PIECE_STATE_IDLE, 8, True, DEFAULT_SHORT_REST_FRAME_COUNT),
        PIECE_STATE_LONG_REST: (0.0, PIECE_STATE_IDLE, 6, True, DEFAULT_LONG_REST_FRAME_COUNT),
    }
    speed_m_per_sec, next_state, frames_per_sec, is_loop, frame_count = defaults_by_state[state_name]
    return PieceStateConfig(
        state_name=state_name,
        speed_m_per_sec=speed_m_per_sec,
        next_state_when_finished=next_state,
        frames_per_sec=frames_per_sec,
        is_loop=is_loop,
        frame_count=frame_count,
    )


def _uniform_move_speed_from_move_time_ms(move_time_ms):
    return (METERS_PER_CELL * MS_PER_SECOND) / move_time_ms


class PieceConfigRegistry:
    def __init__(self, assets_root=None, uniform_move_time_ms=None):
        self._assets_root = pathlib.Path(assets_root) if assets_root else None
        self._uniform_move_time_ms = uniform_move_time_ms
        self._cache = {}

    def get_state_config(self, piece_code, state_name):
        cache_key = (piece_code, state_name)
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load_state_config(piece_code, state_name)
        return self._cache[cache_key]

    def get_travel_speed_m_per_sec(self, piece_code):
        if self._uniform_move_time_ms is not None:
            return _uniform_move_speed_from_move_time_ms(self._uniform_move_time_ms)
        move_config = self.get_state_config(piece_code, PIECE_STATE_MOVE)
        return move_config.speed_m_per_sec

    def get_jump_duration_ms(self, piece_code):
        if self._uniform_move_time_ms is not None:
            from constants import JUMP_DURATION
            return JUMP_DURATION
        jump_config = self.get_state_config(piece_code, PIECE_STATE_JUMP)
        return jump_config.animation_duration_ms()

    def get_rest_duration_ms(self, piece_code, rest_state_name):
        if self._uniform_move_time_ms is not None:
            return 0
        rest_config = self.get_state_config(piece_code, rest_state_name)
        return rest_config.animation_duration_ms()

    def _load_state_config(self, piece_code, state_name):
        if self._assets_root is None:
            return _default_state_config(state_name)

        piece_folder = self._assets_root / piece_code_to_asset_folder(piece_code)
        config_path = piece_folder / "states" / state_name / "config.json"
        if not config_path.is_file():
            return _default_state_config(state_name)

        return _load_state_config_from_disk(piece_folder, state_name)
