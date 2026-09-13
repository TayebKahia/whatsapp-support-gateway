from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from gateway.api.demo import create_demo_router
from gateway.api.webhook import create_webhook_router
from gateway.channel.base import WhatsAppChannelPort
from gateway.channel.meta import MetaCloudAPIAdapter
from gateway.channel.mock import MockWhatsAppAdapter
from gateway.config import Settings
from gateway.config import settings as global_settings
from gateway.engine.processor import MessageProcessor
from gateway.events.dispatcher import OutboundEventDispatcher
from gateway.queue.base import QueuePort
from gateway.queue.in_process import InProcessAsyncQueue
from gateway.repository.idempotency import IdempotencyStore, InMemoryIdempotencyStore
from gateway.repository.order import InMemoryOrderRepository, OrderRepository
from gateway.repository.session import InMemorySessionStore, SessionStore


def create_app(
    app_settings: Settings | None = None,
    idempotency_store: IdempotencyStore | None = None,
    queue: QueuePort | None = None,
    channel: WhatsAppChannelPort | None = None,
    order_repo: OrderRepository | None = None,
    session_store: SessionStore | None = None,
) -> FastAPI:
    cfg = app_settings or global_settings
    idem_store = idempotency_store or InMemoryIdempotencyStore()
    msg_queue = queue or InProcessAsyncQueue()
    repo = order_repo or InMemoryOrderRepository()
    store = session_store or InMemorySessionStore()

    # Determine channel adapter based on settings
    active_channel: WhatsAppChannelPort
    mock_adapter: MockWhatsAppAdapter | None = None

    if channel is not None:
        active_channel = channel
        if isinstance(channel, MockWhatsAppAdapter):
            mock_adapter = channel
    elif cfg.whatsapp_provider == "meta":
        active_channel = MetaCloudAPIAdapter(
            phone_number_id=cfg.phone_number_id,
            access_token=cfg.meta_access_token,
        )
    else:
        mock_adapter = MockWhatsAppAdapter()
        active_channel = mock_adapter

    # Configure external event dispatcher (n8n/Zapier)
    dispatcher: OutboundEventDispatcher | None = None
    if cfg.integration_webhook_url:
        dispatcher = OutboundEventDispatcher(webhook_url=str(cfg.integration_webhook_url))

    processor = MessageProcessor(
        channel=active_channel,
        order_repo=repo,
        session_store=store,
        on_escalation=dispatcher.dispatch_escalation if dispatcher else None,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        # Startup: register message processor on the queue
        msg_queue.start_worker(processor.process_event)
        yield
        # Shutdown: cleanly drain and stop queue workers
        await msg_queue.stop()

    app = FastAPI(
        title="WhatsApp Support Gateway",
        version="0.1.0",
        description="Production WhatsApp Business API Gateway with bounded AI tool-calling and human escalation.",
        lifespan=lifespan,
    )

    # Inbound WhatsApp Webhook Router
    webhook_router = create_webhook_router(
        app_settings=cfg,
        idempotency_store=idem_store,
        queue=msg_queue,
    )
    app.include_router(webhook_router)

    # Embedded Dual-Pane Simulator & Cockpit Router
    demo_router = create_demo_router(
        channel=mock_adapter or MockWhatsAppAdapter(),
        order_repo=repo,
        session_store=store,
        processor=processor,
    )
    app.include_router(demo_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {
            "status": "healthy",
            "environment": cfg.environment,
            "whatsapp_provider": cfg.whatsapp_provider,
        }

    return app


app = create_app()
