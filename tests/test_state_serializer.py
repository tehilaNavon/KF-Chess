import unittest

from client.board_view import BoardView
from models import Position
from server.game.engine_adapter import EngineAdapter
from server.protocol.state_serializer import serialize_game


class TestRestSerialization(unittest.TestCase):
    def _snapshot_after_move(self):
        adapter = EngineAdapter()  # asset-based configs -> real rests occur
        adapter.request_move(Position(7, 1), Position(5, 2))  # wN b1 -> c3
        snapshot = serialize_game(adapter)
        for _ in range(300):
            adapter.advance(16)
            snapshot = serialize_game(adapter)
            if snapshot["rests"]:
                return snapshot
        return snapshot

    def test_rest_is_serialized_after_move(self):
        snapshot = self._snapshot_after_move()
        self.assertTrue(snapshot["rests"], "a rest should be scheduled after a move completes")

    def test_rest_round_trips_into_arbiter(self):
        snapshot = self._snapshot_after_move()
        rest = snapshot["rests"][0]
        arbiter = BoardView._build_arbiter([], [], snapshot["rests"])
        position = Position(*rest["cell"])
        state = arbiter.piece_rest_registry.get_rest_state_name(position, rest["until"] - 1)
        self.assertEqual(state, rest["state"])


if __name__ == "__main__":
    unittest.main()
