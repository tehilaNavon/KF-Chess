"""Message dispatcher. Single concern: route an incoming client message to the
handler registered for its ``type``.

It knows nothing about auth, rooms or the game - other modules register their
own handlers, keeping each feature self-contained.
"""

from __future__ import annotations

import logging
from typing import Awaitable, Callable

from server.protocol.messages import ServerMessage
from server.session import Session

logger = logging.getLogger(__name__)

Handler = Callable[[Session, dict], Awaitable[None]]


class Dispatcher:
    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def register(self, message_type: str, handler: Handler) -> None:
        self._handlers[message_type] = handler

    async def dispatch(self, session: Session, message: dict) -> None:
        message_type = message.get("type")
        handler = self._handlers.get(message_type)
        if handler is None:
            logger.warning("no handler for message type: %s", message_type)
            await session.send(
                ServerMessage.ERROR,
                error="UNKNOWN_MESSAGE",
                received=message_type,
            )
            return
        await handler(session, message.get("payload", {}))
