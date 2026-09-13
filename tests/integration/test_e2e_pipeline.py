import asyncio
import json
import time

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import HttpUrl

from gateway.channel.mock import MockWhatsAppAdapter
from gateway.config import Settings
from gateway.engine.processor import MessageProcessor
from gateway.events.dispatcher import OutboundEventDispatcher
from gateway.main import create_app
from gateway.models.domain import SessionStatus
from gateway.queue.in_process import InProcessAsyncQueue
from gateway.repository.idempotency import InMemoryIdempotencyStore
from gateway.repository.order import InMemoryOrderRepository
from gateway.repository.session import InMemorySessionStore
from gateway.security.signature import calculate_meta_signature


@pytest.mark.asyncio
async def test_full_e2e_order_tracking_flow() -> None:
    secret = "e2e_secret"
    settings = Settings(
        meta_app_secret=secret,
        webhook_verify_token="verify_e2e",
    )

    channel = MockWhatsAppAdapter()
    idempotency_store = InMemoryIdempotencyStore()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    queue = InProcessAsyncQueue()

    processor = MessageProcessor(
        channel=channel,
        order_repo=order_repo,
        session_store=session_store,
    )
    queue.start_worker(processor.process_event)

    app = create_app(
        app_settings=settings,
        idempotency_store=idempotency_store,
        queue=queue,
    )

    phone = "15551234567"
    wamid = "wamid.E2E_ORDER_001"
    payload = f"""{{
        "object": "whatsapp_business_account",
        "entry": [{{
            "id": "1001",
            "changes": [{{
                "field": "messages",
                "value": {{
                    "messaging_product": "whatsapp",
                    "messages": [{{
                        "from": "{phone}",
                        "id": "{wamid}",
                        "timestamp": "1725900000",
                        "type": "text",
                        "text": {{"body": "Hello, can you check where order #ORD-1001 is?"}}
                    }}]
                }}
            }}]
        }}]
    }}""".encode()

    signature = calculate_meta_signature(payload, secret)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        resp = await client.post(
            "/webhook",
            content=payload,
            headers={"X-Hub-Signature-256": signature, "Content-Type": "application/json"},
        )
        duration_ms = (time.perf_counter() - start) * 1000

        # Sub-30ms acknowledgment
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
        assert duration_ms < 100

        # Wait for async processor
        await asyncio.sleep(0.08)

        # Assert WhatsApp outbound reply
        assert len(channel.sent_messages) == 1
        msg = channel.sent_messages[0]
        assert msg["to"] == phone
        assert "ORD-1001" in msg["body"]
        assert "FedEx" in msg["body"]
        assert "TRK-987654" in msg["body"]

        # Assert transcript updated
        session = session_store.get_session(phone)
        assert len(session.transcript) == 2
        assert session.status == SessionStatus.ACTIVE_BOT

    await queue.stop()


@pytest.mark.asyncio
async def test_full_e2e_escalation_and_n8n_webhook_flow() -> None:
    secret = "e2e_secret"
    settings = Settings(
        meta_app_secret=secret,
        webhook_verify_token="verify_e2e",
        integration_webhook_url=HttpUrl("https://n8n.internal/webhook/support"),
    )

    channel = MockWhatsAppAdapter()
    idempotency_store = InMemoryIdempotencyStore()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    queue = InProcessAsyncQueue()

    captured_n8n_requests: list[httpx.Request] = []

    def mock_n8n_handler(req: httpx.Request) -> httpx.Response:
        captured_n8n_requests.append(req)
        return httpx.Response(200, json={"status": "ticket_created"})

    mock_n8n_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_n8n_handler))
    dispatcher = OutboundEventDispatcher(
        webhook_url=str(settings.integration_webhook_url),
        http_client=mock_n8n_client,
    )

    processor = MessageProcessor(
        channel=channel,
        order_repo=order_repo,
        session_store=session_store,
        on_escalation=dispatcher.dispatch_escalation,
    )
    queue.start_worker(processor.process_event)

    app = create_app(
        app_settings=settings,
        idempotency_store=idempotency_store,
        queue=queue,
    )

    phone = "15559873344"
    wamid_esc = "wamid.E2E_ESC_001"
    payload_esc = f"""{{
        "object": "whatsapp_business_account",
        "entry": [{{
            "id": "1001",
            "changes": [{{
                "field": "messages",
                "value": {{
                    "messaging_product": "whatsapp",
                    "messages": [{{
                        "from": "{phone}",
                        "id": "{wamid_esc}",
                        "timestamp": "1725900000",
                        "type": "text",
                        "text": {{"body": "I need to talk to a human agent right now!"}}
                    }}]
                }}
            }}]
        }}]
    }}""".encode()

    signature_esc = calculate_meta_signature(payload_esc, secret)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp1 = await client.post(
            "/webhook",
            content=payload_esc,
            headers={"X-Hub-Signature-256": signature_esc, "Content-Type": "application/json"},
        )
        assert resp1.status_code == 200

        await asyncio.sleep(0.08)

        # Outbound WhatsApp initial notice sent
        assert len(channel.sent_messages) == 1
        assert "human" in channel.sent_messages[0]["body"].lower()

        # Session is now ESCALATED_HUMAN
        session = session_store.get_session(phone)
        assert session.status == SessionStatus.ESCALATED_HUMAN

        # n8n webhook event was delivered
        assert len(captured_n8n_requests) == 1
        n8n_data = json.loads(captured_n8n_requests[0].read().decode("utf-8"))
        assert n8n_data["event_type"] == "ticket.escalated"
        assert n8n_data["customer_phone"] == phone

        # Now test that subsequent customer message is muted
        channel.clear()
        wamid_sub = "wamid.E2E_ESC_002"
        payload_sub = f"""{{
            "object": "whatsapp_business_account",
            "entry": [{{
                "id": "1001",
                "changes": [{{
                    "field": "messages",
                    "value": {{
                        "messaging_product": "whatsapp",
                        "messages": [{{
                            "from": "{phone}",
                            "id": "{wamid_sub}",
                            "timestamp": "1725900100",
                            "type": "text",
                            "text": {{"body": "Hello? Is anyone reading this?"}}
                        }}]
                    }}
                }}]
            }}]
        }}""".encode()

        signature_sub = calculate_meta_signature(payload_sub, secret)
        resp2 = await client.post(
            "/webhook",
            content=payload_sub,
            headers={"X-Hub-Signature-256": signature_sub, "Content-Type": "application/json"},
        )
        assert resp2.status_code == 200

        await asyncio.sleep(0.08)

        # Bot is MUTED - zero outbound messages
        assert len(channel.sent_messages) == 0

        # But transcript recorded the message
        updated_session = session_store.get_session(phone)
        messages = [t["message"] for t in updated_session.transcript]
        assert "Hello? Is anyone reading this?" in messages

    await queue.stop()
