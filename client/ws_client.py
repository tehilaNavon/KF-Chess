"""Synchronous WebSocket client. Single concern: send/receive JSON messages.

Uses the sync client shipped with the ``websockets`` library so it fits a simple
OpenCV loop without asyncio.
"""

from __future__ import annotations

import json
from typing import Optional

from websockets.sync.client import connect

DEFAULT_URL = "ws://127.0.0.1:8000/ws"


class WSClient:
    def __init__(self, url: str = DEFAULT_URL) -> None:
        self._url = url
        self._ws = None

    def connect(self) -> None:
        self._ws = connect(self._url)

    def send(self, message_type: str, **payload) -> None:
        self._ws.send(json.dumps({"type": message_type, "payload": payload}))

    def poll(self, timeout: float = 0.0) -> Optional[dict]:
        """Return the next message, or None if none arrived within ``timeout``."""
        try:
            raw = self._ws.recv(timeout=timeout)
        except TimeoutError:
            return None
        return json.loads(raw)

    def close(self) -> None:
        if self._ws is not None:
            self._ws.close()
            self._ws = None
