import json

import httpx
import pytest

from gateway.channel.meta import MetaCloudAPIAdapter


@pytest.mark.asyncio
async def test_meta_channel_send_text_success() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(
            200,
            json={
                "messaging_product": "whatsapp",
                "contacts": [{"input": "15551234567", "wa_id": "15551234567"}],
                "messages": [{"id": "wamid.OUT001"}],
            },
        )

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    adapter = MetaCloudAPIAdapter(
        phone_number_id="1000123456789",
        access_token="test_access_token",
        http_client=client,
    )

    success = await adapter.send_text("15551234567", "Hello customer!")

    assert success is True
    assert len(captured_requests) == 1
    req = captured_requests[0]
    assert req.method == "POST"
    assert "https://graph.facebook.com/v20.0/1000123456789/messages" in str(req.url)
    assert req.headers["Authorization"] == "Bearer test_access_token"

    data = json.loads(req.read().decode("utf-8"))
    assert data["messaging_product"] == "whatsapp"
    assert data["to"] == "15551234567"
    assert data["type"] == "text"
    assert data["text"]["body"] == "Hello customer!"


@pytest.mark.asyncio
async def test_meta_channel_send_interactive_buttons() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(200, json={"messages": [{"id": "wamid.OUT002"}]})

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    adapter = MetaCloudAPIAdapter(
        phone_number_id="1000123456789",
        access_token="test_access_token",
        http_client=client,
    )

    buttons = [
        {"id": "btn_order", "title": "Track Order"},
        {"id": "btn_human", "title": "Speak with Agent"},
    ]
    success = await adapter.send_interactive_buttons(
        "15551234567", "Please select an option:", buttons
    )

    assert success is True
    assert len(captured_requests) == 1
    req = captured_requests[0]
    data = json.loads(req.read().decode("utf-8"))
    assert data["type"] == "interactive"
    assert data["interactive"]["action"]["buttons"][0]["reply"]["id"] == "btn_order"
    assert data["interactive"]["action"]["buttons"][1]["reply"]["title"] == "Speak with Agent"


@pytest.mark.asyncio
async def test_meta_channel_retry_on_transient_error() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            return httpx.Response(503, json={"error": "Service Temporarily Unavailable"})
        return httpx.Response(200, json={"messages": [{"id": "wamid.OUT003"}]})

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    adapter = MetaCloudAPIAdapter(
        phone_number_id="1000123456789",
        access_token="test_access_token",
        http_client=client,
        max_retries=2,
        initial_backoff_sec=0.01,
    )

    success = await adapter.send_text("15551234567", "Retried message")
    assert success is True
    assert call_count == 2
