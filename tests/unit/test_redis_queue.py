from unittest.mock import AsyncMock

import pytest
from redis.exceptions import ResponseError

from gateway.models.domain import InboundMessageEvent
from gateway.queue.redis_stream import RedisStreamQueue


@pytest.fixture
def mock_redis_client() -> AsyncMock:
    client = AsyncMock()
    client.xadd = AsyncMock(return_value="1000-0")
    client.xgroup_create = AsyncMock(return_value=True)
    client.xack = AsyncMock(return_value=1)
    client.xreadgroup = AsyncMock(return_value=[])
    client.aclose = AsyncMock(return_value=None)
    return client


@pytest.mark.asyncio
async def test_redis_stream_enqueue(mock_redis_client: AsyncMock) -> None:
    queue = RedisStreamQueue(
        redis_client=mock_redis_client,
        stream_key="test:stream",
    )
    event = InboundMessageEvent(
        wamid="wamid.HBgLMTIzNDU2Nzg5MAA=",
        sender_phone="+15551234567",
        body="Track my package",
        interactive_id=None,
        timestamp="1710374400",
    )

    await queue.enqueue(event)

    mock_redis_client.xadd.assert_awaited_once()
    args, _ = mock_redis_client.xadd.call_args
    assert args[0] == "test:stream"
    assert "payload" in args[1]
    assert "Track my package" in args[1]["payload"]


@pytest.mark.asyncio
async def test_redis_stream_worker_consumes_and_acks(mock_redis_client: AsyncMock) -> None:
    event = InboundMessageEvent(
        wamid="wamid.HBgLMTIzNDU2Nzg5MAA=",
        sender_phone="+15551234567",
        body="Track my package",
        interactive_id=None,
        timestamp="1710374400",
    )

    # First call returns a message, second call returns empty list
    mock_redis_client.xreadgroup.side_effect = [
        [
            (
                "test:stream",
                [
                    (
                        "1710374400-0",
                        {"payload": event.model_dump_json()},
                    )
                ],
            )
        ],
        [],
    ]

    processed_events: list[InboundMessageEvent] = []

    async def sample_handler(e: InboundMessageEvent) -> None:
        processed_events.append(e)

    queue = RedisStreamQueue(
        redis_client=mock_redis_client,
        stream_key="test:stream",
        consumer_group="test_group",
        consumer_name="worker_test",
        poll_interval_ms=10,
    )

    queue.start_worker(sample_handler)
    # Start worker loop manually or await worker task
    task = queue._worker_task
    assert task is not None

    # Wait briefly for worker to consume
    import asyncio

    for _ in range(10):
        if processed_events:
            break
        await asyncio.sleep(0.05)

    await queue.stop()

    assert len(processed_events) == 1
    assert processed_events[0].wamid == event.wamid
    mock_redis_client.xgroup_create.assert_awaited_once_with(
        "test:stream", "test_group", id="0", mkstream=True
    )
    mock_redis_client.xack.assert_awaited_once_with("test:stream", "test_group", "1710374400-0")


@pytest.mark.asyncio
async def test_redis_stream_handles_busygroup(mock_redis_client: AsyncMock) -> None:
    mock_redis_client.xgroup_create.side_effect = ResponseError(
        "BUSYGROUP Consumer Group name already exists"
    )
    mock_redis_client.xreadgroup.return_value = []

    queue = RedisStreamQueue(
        redis_client=mock_redis_client,
        stream_key="test:stream",
        consumer_group="test_group",
    )

    # Should not raise exception
    await queue._init_consumer_group(mock_redis_client)
    mock_redis_client.xgroup_create.assert_awaited_once()
