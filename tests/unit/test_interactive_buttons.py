import pytest

from gateway.channel.mock import MockWhatsAppAdapter
from gateway.engine.processor import MessageProcessor
from gateway.models.domain import InboundMessageEvent
from gateway.repository.order import InMemoryOrderRepository
from gateway.repository.session import InMemorySessionStore


@pytest.mark.asyncio
async def test_processor_dispatches_interactive_buttons_on_menu() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    processor = MessageProcessor(channel, order_repo, session_store)

    event = InboundMessageEvent(
        wamid="wamid.1",
        sender_phone="15551234567",
        body="menu",
        timestamp="1000",
    )
    await processor.process_event(event)

    assert len(channel.sent_messages) == 1
    msg = channel.sent_messages[0]
    assert msg["type"] == "interactive"
    assert "buttons" in msg
    assert len(msg["buttons"]) == 3
    assert msg["buttons"][0]["id"] == "btn_track"


@pytest.mark.asyncio
async def test_processor_dispatches_interactive_buttons_on_order_status() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    processor = MessageProcessor(channel, order_repo, session_store)

    # 15551234567 owns ORD-1001
    event = InboundMessageEvent(
        wamid="wamid.2",
        sender_phone="15551234567",
        body="Where is ORD-1001?",
        timestamp="1000",
    )
    await processor.process_event(event)

    assert len(channel.sent_messages) == 1
    msg = channel.sent_messages[0]
    assert msg["type"] == "interactive"
    assert "buttons" in msg
    assert any(b["id"] == "btn_return" for b in msg["buttons"])
    assert any(b["id"] == "btn_human" for b in msg["buttons"])


@pytest.mark.asyncio
async def test_processor_handles_interactive_button_click() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    processor = MessageProcessor(channel, order_repo, session_store)

    event = InboundMessageEvent(
        wamid="wamid.3",
        sender_phone="15551234567",
        body="Return / Refund",
        interactive_id="btn_return",
        timestamp="1000",
    )
    await processor.process_event(event)

    assert len(channel.sent_messages) == 1
    msg = channel.sent_messages[0]
    # Prompt for return order number or instructions
    assert "return" in msg["body"].lower()
