import pytest

from gateway.channel.mock import MockWhatsAppAdapter


@pytest.mark.asyncio
async def test_mock_channel_send_text() -> None:
    adapter = MockWhatsAppAdapter()
    success = await adapter.send_text("15551234567", "Hello from support!")

    assert success is True
    assert len(adapter.sent_messages) == 1
    assert adapter.sent_messages[0]["to"] == "15551234567"
    assert adapter.sent_messages[0]["type"] == "text"
    assert adapter.sent_messages[0]["body"] == "Hello from support!"


@pytest.mark.asyncio
async def test_mock_channel_send_interactive_buttons() -> None:
    adapter = MockWhatsAppAdapter()
    buttons = [
        {"id": "btn_order", "title": "Track Order"},
        {"id": "btn_human", "title": "Talk to Human"},
    ]
    success = await adapter.send_interactive_buttons(
        "15551234567", "How can we help you today?", buttons
    )

    assert success is True
    assert len(adapter.sent_messages) == 1
    assert adapter.sent_messages[0]["type"] == "interactive"
    assert adapter.sent_messages[0]["buttons"] == buttons


@pytest.mark.asyncio
async def test_mock_channel_clear() -> None:
    adapter = MockWhatsAppAdapter()
    await adapter.send_text("15551234567", "msg 1")
    assert len(adapter.sent_messages) == 1
    adapter.clear()
    assert len(adapter.sent_messages) == 0
