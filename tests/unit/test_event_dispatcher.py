import json

import httpx
import pytest

from gateway.events.dispatcher import OutboundEventDispatcher
from gateway.models.domain import SessionRecord, SessionStatus


@pytest.mark.asyncio
async def test_event_dispatcher_disabled_when_no_url() -> None:
    dispatcher = OutboundEventDispatcher(webhook_url=None)
    session = SessionRecord(
        phone_number="15551234567",
        status=SessionStatus.ESCALATED_HUMAN,
        last_interaction_ts=1000.0,
    )

    success = await dispatcher.dispatch_escalation(session, reason="User requested agent")
    assert success is False


@pytest.mark.asyncio
async def test_event_dispatcher_fires_valid_payload() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(200, json={"received": True})

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    dispatcher = OutboundEventDispatcher(
        webhook_url="https://n8n.internal/webhook/escalation",
        http_client=client,
    )

    session = SessionRecord(
        phone_number="15551234567",
        status=SessionStatus.ESCALATED_HUMAN,
        transcript=[
            {"role": "user", "message": "My item is defective"},
            {"role": "assistant", "message": "I will connect you to our support team"},
        ],
        last_interaction_ts=1000.0,
    )

    success = await dispatcher.dispatch_escalation(session, reason="Defective product complaint")
    assert success is True
    assert len(captured_requests) == 1

    req = captured_requests[0]
    assert req.method == "POST"
    assert str(req.url) == "https://n8n.internal/webhook/escalation"

    data = json.loads(req.read().decode("utf-8"))
    assert data["event_type"] == "ticket.escalated"
    assert data["customer_phone"] == "15551234567"
    assert data["reason"] == "Defective product complaint"
    assert len(data["conversation_snippet"]) == 2


@pytest.mark.asyncio
async def test_event_dispatcher_handles_network_failure_gracefully() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Could not reach n8n server")

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    dispatcher = OutboundEventDispatcher(
        webhook_url="https://n8n.unreachable/webhook",
        http_client=client,
        max_retries=1,
    )

    session = SessionRecord(
        phone_number="15551234567",
        status=SessionStatus.ESCALATED_HUMAN,
        last_interaction_ts=1000.0,
    )

    # Must NOT raise exception; returns False and logs error
    success = await dispatcher.dispatch_escalation(session, reason="Urgent help")
    assert success is False
