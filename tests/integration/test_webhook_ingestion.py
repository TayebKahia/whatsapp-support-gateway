import asyncio
import time

import pytest
from httpx import ASGITransport, AsyncClient

from gateway.config import Settings
from gateway.main import create_app
from gateway.models.domain import InboundMessageEvent
from gateway.queue.in_process import InProcessAsyncQueue
from gateway.repository.idempotency import InMemoryIdempotencyStore
from gateway.security.signature import calculate_meta_signature


@pytest.mark.asyncio
async def test_webhook_ingestion_and_idempotency() -> None:
    secret = "test_app_secret"
    settings = Settings(
        meta_app_secret=secret,
        webhook_verify_token="test_verify_token",
    )

    idempotency_store = InMemoryIdempotencyStore()
    queue = InProcessAsyncQueue()
    enqueued_events: list[InboundMessageEvent] = []

    async def test_worker(event: InboundMessageEvent) -> None:
        enqueued_events.append(event)

    queue.start_worker(test_worker)

    app = create_app(
        app_settings=settings,
        idempotency_store=idempotency_store,
        queue=queue,
    )

    wamid = "wamid.IDEMPOTENT_TEST_99"
    payload = f"""{{
        "object": "whatsapp_business_account",
        "entry": [{{
            "id": "10001",
            "changes": [{{
                "field": "messages",
                "value": {{
                    "messaging_product": "whatsapp",
                    "messages": [{{
                        "from": "15559998888",
                        "id": "{wamid}",
                        "timestamp": "1725900000",
                        "type": "text",
                        "text": {{"body": "Where is my package?"}}
                    }}]
                }}
            }}]
        }}]
    }}""".encode()

    signature = calculate_meta_signature(payload, secret)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First delivery: Should process and enqueue
        start_time = time.perf_counter()
        response1 = await client.post(
            "/webhook",
            content=payload,
            headers={"X-Hub-Signature-256": signature, "Content-Type": "application/json"},
        )
        duration_ms = (time.perf_counter() - start_time) * 1000

        assert response1.status_code == 200
        assert response1.json() == {"status": "ok"}
        # Meta requires < 3000ms; we target sub-30ms
        assert duration_ms < 100

        # Wait for queue worker to pick up
        await asyncio.sleep(0.05)
        assert len(enqueued_events) == 1
        assert enqueued_events[0].wamid == wamid
        assert enqueued_events[0].sender_phone == "15559998888"
        assert enqueued_events[0].body == "Where is my package?"

        # Second delivery with identical WAMID (simulating Meta retry)
        response2 = await client.post(
            "/webhook",
            content=payload,
            headers={"X-Hub-Signature-256": signature, "Content-Type": "application/json"},
        )
        assert response2.status_code == 200
        assert response2.json() == {"status": "ok"}

        await asyncio.sleep(0.05)
        # Event count must STILL be 1 (duplicate dropped by idempotency filter)
        assert len(enqueued_events) == 1

    await queue.stop()
