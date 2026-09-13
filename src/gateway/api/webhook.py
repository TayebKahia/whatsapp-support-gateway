from fastapi import APIRouter, Header, HTTPException, Query, Request, Response, status
from pydantic import ValidationError

from gateway.config import Settings
from gateway.config import settings as global_settings
from gateway.models.domain import InboundMessageEvent
from gateway.models.webhook import MetaWebhookPayload, WhatsAppMessageType
from gateway.queue.base import QueuePort
from gateway.repository.idempotency import IdempotencyStore, InMemoryIdempotencyStore
from gateway.security.signature import verify_meta_signature


def create_webhook_router(
    app_settings: Settings | None = None,
    idempotency_store: IdempotencyStore | None = None,
    queue: QueuePort | None = None,
) -> APIRouter:
    cfg = app_settings or global_settings
    idem_store = idempotency_store or InMemoryIdempotencyStore()
    router = APIRouter()

    @router.get("/webhook")
    async def verify_webhook_handshake(
        hub_mode: str = Query(alias="hub.mode"),
        hub_verify_token: str = Query(alias="hub.verify_token"),
        hub_challenge: str = Query(alias="hub.challenge"),
    ) -> Response:
        """Meta WhatsApp Cloud API webhook handshake verification endpoint."""
        if hub_mode == "subscribe" and hub_verify_token == cfg.webhook_verify_token:
            return Response(
                content=hub_challenge, media_type="text/plain", status_code=status.HTTP_200_OK
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verification token or mode mismatch",
        )

    @router.post("/webhook")
    async def receive_webhook(
        request: Request,
        x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
    ) -> dict[str, str]:
        """Inbound WhatsApp webhook endpoint with cryptographic signature validation & async enqueue."""
        raw_body = await request.body()

        if not verify_meta_signature(raw_body, x_hub_signature_256, cfg.meta_app_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid cryptographic payload signature",
            )

        try:
            payload = MetaWebhookPayload.model_validate_json(raw_body)
        except (ValidationError, ValueError):
            # Return 200 to acknowledge non-message events (e.g. read receipts or status updates)
            return {"status": "ignored"}

        # Fast normalization, idempotency check, and enqueue
        for entry in payload.entry:
            for change in entry.changes:
                for msg in change.value.messages:
                    if idem_store.is_processed(msg.id):
                        continue

                    idem_store.mark_processed(msg.id)

                    body: str | None = None
                    interactive_id: str | None = None

                    if msg.type == WhatsAppMessageType.TEXT and msg.text:
                        body = msg.text.body
                    elif (
                        msg.type == WhatsAppMessageType.INTERACTIVE
                        and msg.interactive
                        and msg.interactive.button_reply
                    ):
                        body = msg.interactive.button_reply.title
                        interactive_id = msg.interactive.button_reply.id
                    elif msg.text:
                        body = msg.text.body

                    if body and queue:
                        event = InboundMessageEvent(
                            wamid=msg.id,
                            sender_phone=msg.from_number,
                            body=body,
                            interactive_id=interactive_id,
                            timestamp=msg.timestamp,
                        )
                        await queue.enqueue(event)

        return {"status": "ok"}

    return router
