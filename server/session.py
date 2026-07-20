"""Session: the authenticated identity and game context of one client.

Single concern: hold *who* a connection is (user) and *where* they are (room,
role). It does not read sockets and does not run auth rules - it only carries
state and offers a thin ``send`` helper.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from server.auth.users import UserRecord

if TYPE_CHECKING:  # avoid a runtime import cycle with the transport layer
    from server.transport.ws_server import Connection

ROLE_WHITE = "white"
ROLE_BLACK = "black"
ROLE_VIEWER = "viewer"


class Session:
    def __init__(self, connection: "Connection") -> None:
        self._connection = connection
        self.user: Optional[UserRecord] = None
        self.room_id: Optional[str] = None
        self.role: Optional[str] = None

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None

    def authenticate(self, user: UserRecord) -> None:
        self.user = user

    async def send(self, message_type: str, **payload) -> None:
        await self._connection.send({"type": message_type, "payload": payload})
