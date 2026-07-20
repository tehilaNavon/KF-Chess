import unittest

from starlette.testclient import TestClient

from server.app import create_app
from server.protocol.messages import ClientMessage, ServerMessage


class TestLoginFlow(unittest.TestCase):
    def setUp(self):
        self.app = create_app(db_path=":memory:")
        self.client = TestClient(self.app)
        self.client.__enter__()  # triggers lifespan -> database.connect()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def _send(self, ws, message_type, **payload):
        ws.send_json({"type": message_type, "payload": payload})
        return ws.receive_json()

    def test_register_then_login(self):
        with self.client.websocket_connect("/ws") as ws:
            registered = self._send(
                ws, ClientMessage.REGISTER, username="alice", password="pass"
            )
            self.assertEqual(registered["type"], ServerMessage.AUTH_OK)
            self.assertEqual(registered["payload"]["username"], "alice")
            self.assertEqual(registered["payload"]["rating"], 1200)

            logged_in = self._send(
                ws, ClientMessage.LOGIN, username="alice", password="pass"
            )
            self.assertEqual(logged_in["type"], ServerMessage.AUTH_OK)

    def test_login_wrong_password(self):
        with self.client.websocket_connect("/ws") as ws:
            self._send(ws, ClientMessage.REGISTER, username="bob", password="pass")
            reply = self._send(
                ws, ClientMessage.LOGIN, username="bob", password="nope"
            )
            self.assertEqual(reply["type"], ServerMessage.AUTH_ERR)
            self.assertEqual(reply["payload"]["error"], "INVALID_CREDENTIALS")

    def test_unknown_message_type(self):
        with self.client.websocket_connect("/ws") as ws:
            reply = self._send(ws, "NONSENSE")
            self.assertEqual(reply["type"], ServerMessage.ERROR)
            self.assertEqual(reply["payload"]["error"], "UNKNOWN_MESSAGE")


if __name__ == "__main__":
    unittest.main()
