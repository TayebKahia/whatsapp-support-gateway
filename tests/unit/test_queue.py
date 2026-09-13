import asyncio

import pytest

from gateway.models.domain import InboundMessageEvent
from gateway.queue.in_process import InProcessAsyncQueue


@pytest.mark.asyncio
async def test_in_process_async_queue_dispatch() -> None:
    queue = InProcessAsyncQueue()
    received_events: list[InboundMessageEvent] = []

    async def mock_handler(event: InboundMessageEvent) -> None:
        received_events.append(event)

    queue.start_worker(mock_handler)

    test_event = InboundMessageEvent(
        wamid="wamid.Q001",
        sender_phone="15551234567",
        body="Order status please",
        timestamp="1725900000",
    )

    await queue.enqueue(test_event)

    # Wait briefly for the worker to process the queued event
    await asyncio.sleep(0.05)
    await queue.stop()

    assert len(received_events) == 1
    assert received_events[0].wamid == "wamid.Q001"
    assert received_events[0].body == "Order status please"
