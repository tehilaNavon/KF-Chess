import unittest

from starlette.testclient import TestClient

from server.app import create_app
from server.protocol.messages import ClientMessage, ServerMessage


class TestBasicGameOverWebSocket(unittest.TestCase):
    def setUp(self):
        # Large snapshot interval so periodic broadcasts do not interfere;
        # we rely on the immediate broadcast that follows a successful move.
        self.app = create_app(
            db_path=":memory:",
            snapshot_interval_ms=1_000_000,
            move_time=1000,
        )
        self.client = TestClient(self.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def _login_and_join(self, ws, username):
        ws.send_json(
            {"type": ClientMessage.REGISTER, "payload": {"username": username, "password": "pass"}}
        )
        self.assertEqual(ws.receive_json()["type"], ServerMessage.AUTH_OK)
        ws.send_json({"type": ClientMessage.JOIN_GAME, "payload": {}})
        seated = ws.receive_json()
        snapshot = ws.receive_json()
        self.assertEqual(seated["type"], ServerMessage.SEATED)
        self.assertEqual(snapshot["type"], ServerMessage.STATE_SNAPSHOT)
        return seated

    def test_first_player_is_white_and_can_move(self):
        with self.client.websocket_connect("/ws") as ws:
            seated = self._login_and_join(ws, "alice")
            self.assertEqual(seated["payload"]["color"], "w")

            ws.send_json({"type": ClientMessage.COMMAND, "payload": {"cmd": "WNb1c3"}})
            message = ws.receive_json()
            self.assertEqual(message["type"], ServerMessage.STATE_SNAPSHOT)
            self.assertGreaterEqual(len(message["payload"]["motions"]), 1)

    def test_cannot_move_opponent_color(self):
        with self.client.websocket_connect("/ws") as ws:
            self._login_and_join(ws, "bob")
            ws.send_json({"type": ClientMessage.COMMAND, "payload": {"cmd": "bNb8c6"}})
            message = ws.receive_json()
            self.assertEqual(message["type"], ServerMessage.MOVE_REJECTED)
            self.assertEqual(message["payload"]["reason"], "NOT_YOUR_COLOR")


if __name__ == "__main__":
    unittest.main()
