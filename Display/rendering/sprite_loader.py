import cv2

from Display.rendering.img import Img
from Display.rendering.sprite_paths import build_sprite_path


class SpriteLoader:
    def __init__(self, pieces_root, cell_size):
        self._pieces_root = pieces_root
        self._cell_size = cell_size
        self._sprite_cache = {}

    def load_idle_sprite(self, piece_code):
        return self.load_sprite(piece_code, "idle", frame_number=1)

    def load_sprite(self, piece_code, state_name, frame_number=1):
        cache_key = (piece_code, state_name, frame_number)
        if cache_key not in self._sprite_cache:
            self._sprite_cache[cache_key] = self._read_sprite(piece_code, state_name, frame_number)
        return self._sprite_cache[cache_key]

    def _read_sprite(self, piece_code, state_name, frame_number):
        sprite_path = build_sprite_path(self._pieces_root, piece_code, state_name, frame_number)
        sprite_size = (self._cell_size, self._cell_size)
        return Img().read(sprite_path, size=sprite_size, keep_aspect=True, interpolation=cv2.INTER_AREA)
