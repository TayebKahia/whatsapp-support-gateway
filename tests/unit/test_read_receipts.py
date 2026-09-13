from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from gateway.channel.meta import MetaCloudAPIAdapter
from gateway.channel.mock import MockWhatsAppAdapter
from gateway.engine.processor import MessageProcessor
from gateway.models.domain import InboundMessageEvent
from gateway.repository.order import InMemoryOrderRepository
from gateway.repository.session import InMemorySessionStore


@pytest.mark.asyncio
async def test_mock_channel_mark_read() -> None:
    adapter = MockWhatsAppAdapter()
    success = await adapter.mark_read("wamid.HBgLMTU1NTEyMzQ1NjcVAgASGBQzQT...")
    assert success is True
    assert len(adapter.read_wamids) == 1
    assert adapter.read_wamids[0] == "wamid.HBgLMTU1NTEyMzQ1NjcVAgASGBQzQT..."

    adapter.clear()
    assert len(adapter.read_wamids) == 0


@pytest.mark.asyncio
async def test_meta_channel_mark_read() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = AsyncClient()
    mock_client.post = AsyncMock(return_value=mock_response)  # type: ignore[method-assign]

    adapter = MetaCloudAPIAdapter(
        phone_number_id="1000999888",
        access_token="fake_token",
        http_client=mock_client,
    )

    success = await adapter.mark_read("wamid.HBgLMTU1NTEyMzQ1NjcVAgASGBQzQT...")
    assert success is True
    mock_client.post.assert_called_once()
    payload = mock_client.post.call_args[1]["json"]
    assert payload["status"] == "read"
    assert payload["message_id"] == "wamid.HBgLMTU1NTEyMzQ1NjcVAgASGBQzQT..."


@pytest.mark.asyncio
async def test_processor_automatically_marks_message_read() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    processor = MessageProcessor(channel, order_repo, session_store)

    event = InboundMessageEvent(
        wamid="wamid.MSG_TO_READ_123",
        sender_phone="15551234567",
        body="menu",
        timestamp="1000",
    )
    await processor.process_event(event)

    assert "wamid.MSG_TO_READ_123" in channel.read_wamids
