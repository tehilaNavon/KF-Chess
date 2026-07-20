"""In-process asynchronous publish/subscribe bus.

The bus is the internal backbone of the server: components publish events to
named topics and never talk to each other directly. A publisher does not know
(or care) who is listening, and a subscriber does not know who produced the
event. This keeps the game engine, transport, ELO service and loggers fully
decoupled.

Every event optionally carries a ``room_id`` so subscribers can listen only to
the game room they care about.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Event:
    """A single message flowing through the bus."""

    topic: str
    payload: dict = field(default_factory=dict)
    room_id: Optional[str] = None


Handler = Callable[[Event], Awaitable[None]]


@dataclass
class Subscription:
    """Handle returned by :meth:`Bus.subscribe`; call ``unsubscribe`` to detach."""

    topic: str
    handler: Handler
    room_id: Optional[str]
    _bus: "Bus"

    def unsubscribe(self) -> None:
        self._bus._remove(self)


class Bus:
    """Asynchronous topic-based pub/sub, safe to use on a single event loop."""

    WILDCARD = "*"

    def __init__(self) -> None:
        self._subscriptions: dict[str, list[Subscription]] = {}

    def subscribe(
        self,
        topic: str,
        handler: Handler,
        room_id: Optional[str] = None,
    ) -> Subscription:
        """Register ``handler`` for ``topic``.

        If ``room_id`` is given, the handler only receives events whose
        ``room_id`` matches (events with a different room are skipped).
        """
        subscription = Subscription(topic, handler, room_id, self)
        self._subscriptions.setdefault(topic, []).append(subscription)
        return subscription

    def subscribe_all(
        self,
        handler: Handler,
        room_id: Optional[str] = None,
    ) -> Subscription:
        """Register ``handler`` for every topic (useful for loggers)."""
        return self.subscribe(self.WILDCARD, handler, room_id)

    async def publish(self, event: Event) -> None:
        """Deliver ``event`` to all matching handlers concurrently.

        A failing handler is logged and isolated, so one broken subscriber can
        never stop the others from receiving the event.
        """
        handlers = self._collect_handlers(event)
        if not handlers:
            return
        await asyncio.gather(
            *(self._safe_call(handler, event) for handler in handlers)
        )

    async def emit(
        self,
        topic: str,
        room_id: Optional[str] = None,
        **payload,
    ) -> None:
        """Convenience wrapper that builds an :class:`Event` and publishes it."""
        await self.publish(Event(topic=topic, payload=payload, room_id=room_id))

    def _collect_handlers(self, event: Event) -> list[Handler]:
        matched: list[Handler] = []
        for topic in (event.topic, self.WILDCARD):
            for subscription in self._subscriptions.get(topic, ()):
                if self._matches(subscription, event):
                    matched.append(subscription.handler)
        return matched

    @staticmethod
    def _matches(subscription: Subscription, event: Event) -> bool:
        if subscription.room_id is None:
            return True
        return subscription.room_id == event.room_id

    async def _safe_call(self, handler: Handler, event: Event) -> None:
        try:
            await handler(event)
        except Exception:  # noqa: BLE001 - isolate faulty subscribers
            logger.exception("Bus handler failed for topic '%s'", event.topic)

    def _remove(self, subscription: Subscription) -> None:
        subscriptions = self._subscriptions.get(subscription.topic)
        if not subscriptions:
            return
        if subscription in subscriptions:
            subscriptions.remove(subscription)
        if not subscriptions:
            del self._subscriptions[subscription.topic]
