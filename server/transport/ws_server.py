"""WebSocket transport: bridges client sockets and the internal bus.

Each browser/GUI client owns one :class:`Connection`. A connection does two
things:

1. Reads JSON messages coming *from* the client and republishes them onto the
   bus, so the rest of the server can react without knowing about sockets.
2. Subscribes *to* the bus and forwards every matching event back *to* the
   client as JSON.

That is the full round trip: client -> ws -> bus -> ws -> client.
"""

from __future__ import annotations

import logging
from itertools import count
from typing import Optional

from starlette.websockets import WebSocket, WebSocketDisconnect

from server.bus import Bus, Event, Subscription
from server.dispatcher import Dispatcher
from server.session import Session

logger = logging.getLogger(__name__)


class Connection:
    """A single client socket wired to the bus."""

    def __init__(self, websocket: WebSocket, bus: Bus, connection_id: str) -> None:
        self.websocket = websocket
        self.bus = bus
        self.connection_id = connection_id
        self.room_id: Optional[str] = None
        self._subscription: Optional[Subscription] = None

    async def send(self, message: dict) -> None:
        await self.websocket.send_json(message)

    async def _forward_event(self, event: Event) -> None:
        """Bus handler: push a bus event down to this client."""
        await self.send(
            {
                "type": event.topic,
                "room_id": event.room_id,
                "payload": event.payload,
            }
        )

    def bind_bus(self) -> None:
        """Start forwarding bus events to this client.

        For now the connection listens to every event; once rooms exist it will
        re-bind scoped to its own ``room_id``.
        """
        self._subscription = self.bus.subscribe_all(self._forward_event)

    def unbind_bus(self) -> None:
        if self._subscription is not None:
            self._subscription.unsubscribe()
            self._subscription = None


class ConnectionManager:
    """Tracks live connections and their lifecycle."""

    def __init__(self, bus: Bus) -> None:
        self.bus = bus
        self._connections: dict[str, Connection] = {}
        self._ids = count(1)

    async def connect(self, websocket: WebSocket) -> Connection:
        await websocket.accept()
        connection = Connection(websocket, self.bus, f"conn-{next(self._ids)}")
        self._connections[connection.connection_id] = connection
        connection.bind_bus()
        logger.info("client connected: %s", connection.connection_id)
        return connection

    async def disconnect(self, connection: Connection) -> None:
        connection.unbind_bus()
        self._connections.pop(connection.connection_id, None)
        logger.info("client disconnected: %s", connection.connection_id)

    @property
    def count(self) -> int:
        return len(self._connections)


async def websocket_handler(
    websocket: WebSocket,
    manager: ConnectionManager,
    dispatcher: Dispatcher,
) -> None:
    """Endpoint loop: accept a client, then route each message via the dispatcher."""
    connection = await manager.connect(websocket)
    session = Session(connection)
    try:
        while True:
            message = await websocket.receive_json()
            await dispatcher.dispatch(session, message)
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(connection)
