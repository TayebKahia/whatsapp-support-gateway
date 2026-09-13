from collections.abc import Awaitable, Callable
from typing import Protocol

from gateway.models.domain import InboundMessageEvent

EventHandler = Callable[[InboundMessageEvent], Awaitable[None]]


class QueuePort(Protocol):
    """Port defining the asynchronous queue interface."""

    async def enqueue(self, event: InboundMessageEvent) -> None:
        """Enqueue an inbound message event for background processing."""
        ...

    def start_worker(self, handler: EventHandler) -> None:
        """Register the message processor callback and begin background worker loop."""
        ...

    async def stop(self) -> None:
        """Gracefully drain remaining messages and stop background workers."""
        ...
