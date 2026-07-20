"""Home screen in the shell: log in / register, then join the game.

Single concern: the pre-game console flow. Once seated it hands control to the
board view.
"""

from __future__ import annotations

import time
from typing import Optional

from client.board_view import BoardView
from client.ws_client import DEFAULT_URL, WSClient
from server.protocol.messages import ClientMessage, ServerMessage


def run(url: str = DEFAULT_URL) -> None:
    client = WSClient(url)
    client.connect()
    if not _authenticate(client):
        client.close()
        return

    client.send(ClientMessage.JOIN_GAME)
    seated = _wait_for(client, ServerMessage.SEATED)
    color = seated["payload"]["color"] if seated else None
    print(f"You are: {color or 'viewer'}")

    BoardView(client, color).run()


def _authenticate(client: WSClient) -> bool:
    while True:
        action = input("(l)ogin or (r)egister? ").strip().lower()
        username = input("username: ").strip()
        password = input("password: ").strip()
        message_type = (
            ClientMessage.REGISTER if action.startswith("r") else ClientMessage.LOGIN
        )
        client.send(message_type, username=username, password=password)

        reply = _wait_for(client, ServerMessage.AUTH_OK, ServerMessage.AUTH_ERR)
        if reply and reply["type"] == ServerMessage.AUTH_OK:
            print(f"Logged in. Rating: {reply['payload']['rating']}")
            return True
        error = reply["payload"].get("error") if reply else "no response"
        print(f"Auth failed: {error}")


def _wait_for(client: WSClient, *types: str, timeout: float = 5.0) -> Optional[dict]:
    """Return the next message of one of ``types``, skipping others (e.g. the
    periodic state broadcasts) until one arrives or ``timeout`` elapses.
    """
    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        message = client.poll(timeout=remaining)
        if message is None:
            return None
        if not types or message["type"] in types:
            return message


if __name__ == "__main__":
    run()
