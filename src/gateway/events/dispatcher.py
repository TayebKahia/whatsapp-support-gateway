import logging
from datetime import UTC, datetime

import httpx

from gateway.models.domain import SessionRecord
from gateway.models.events import EscalationEventPayload

logger = logging.getLogger(__name__)


class OutboundEventDispatcher:
    """Delivers structured event payloads to external automation webhooks (n8n, Make, Zapier)."""

    def __init__(
        self,
        webhook_url: str | None = None,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int = 2,
    ) -> None:
        self.webhook_url = webhook_url
        self._client = http_client
        self.max_retries = max_retries

    async def dispatch_escalation(self, session: SessionRecord, reason: str) -> bool:
        if not self.webhook_url:
            logger.debug("Outbound escalation event skipped (no webhook URL configured).")
            return False

        payload = EscalationEventPayload(
            customer_phone=session.phone_number,
            reason=reason,
            timestamp=datetime.now(UTC).isoformat(),
            conversation_snippet=session.transcript[-5:],
        )

        client = self._client or httpx.AsyncClient(timeout=5.0)
        should_close = self._client is None

        try:
            for attempt in range(1, self.max_retries + 1):
                try:
                    response = await client.post(
                        self.webhook_url,
                        json=payload.model_dump(),
                        headers={"Content-Type": "application/json"},
                    )
                    if response.status_code in (200, 201, 202, 204):
                        logger.info(
                            "Successfully delivered escalation event for %s to %s",
                            session.phone_number,
                            self.webhook_url,
                        )
                        return True

                    logger.warning(
                        "External webhook returned HTTP %d on attempt %d",
                        response.status_code,
                        attempt,
                    )
                except httpx.HTTPError as exc:
                    logger.warning(
                        "HTTP error delivering escalation event on attempt %d: %s",
                        attempt,
                        exc,
                    )
            return False
        finally:
            if should_close:
                await client.aclose()
