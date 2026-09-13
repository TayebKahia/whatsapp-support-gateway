from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from gateway.channel.meta import MetaCloudAPIAdapter
from gateway.channel.mock import MockWhatsAppAdapter


@pytest.mark.asyncio
async def test_mock_channel_send_document() -> None:
    channel = MockWhatsAppAdapter()
    success = await channel.send_document(
        to_phone="15551234567",
        document_url="https://api.example.com/media/return-labels/ORD-1003.pdf",
        filename="return_label_ORD-1003.pdf",
        caption="Prepaid Return Shipping Label",
    )

    assert success is True
    assert len(channel.sent_messages) == 1
    msg = channel.sent_messages[0]
    assert msg["type"] == "document"
    assert msg["to"] == "15551234567"
    assert "ORD-1003.pdf" in msg["document_url"]
    assert msg["filename"] == "return_label_ORD-1003.pdf"
    assert msg["caption"] == "Prepaid Return Shipping Label"


@pytest.mark.asyncio
async def test_meta_channel_send_document() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = AsyncClient()
    mock_client.post = AsyncMock(return_value=mock_response)  # type: ignore[method-assign]

    adapter = MetaCloudAPIAdapter(
        phone_number_id="1000999888",
        access_token="fake_token",
        http_client=mock_client,
    )

    success = await adapter.send_document(
        to_phone="15551234567",
        document_url="https://api.example.com/media/return-labels/ORD-1003.pdf",
        filename="return_label_ORD-1003.pdf",
        caption="Here is your label",
    )

    assert success is True
    mock_client.post.assert_called_once()
    payload = mock_client.post.call_args[1]["json"]
    assert payload["type"] == "document"
    assert payload["document"]["link"] == "https://api.example.com/media/return-labels/ORD-1003.pdf"
    assert payload["document"]["filename"] == "return_label_ORD-1003.pdf"
    assert payload["document"]["caption"] == "Here is your label"
