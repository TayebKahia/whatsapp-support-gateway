import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class MetaCloudAPIAdapter:
    """Production adapter communicating with Meta WhatsApp Business Cloud API (Graph API v20.0+)."""

    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        api_version: str = "v20.0",
        http_client: httpx.AsyncClient | None = None,
        max_retries: int = 3,
        initial_backoff_sec: float = 0.5,
    ) -> None:
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
        self._client = http_client
        self.max_retries = max_retries
        self.initial_backoff_sec = initial_backoff_sec

    async def _post_with_retry(self, payload: dict[str, Any]) -> bool:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        client = self._client or httpx.AsyncClient(timeout=10.0)
        should_close = self._client is None

        try:
            backoff = self.initial_backoff_sec
            for attempt in range(1, self.max_retries + 1):
                try:
                    response = await client.post(self.base_url, json=payload, headers=headers)
                    if response.status_code in (200, 201):
                        return True

                    if (
                        response.status_code in (429, 500, 502, 503, 504)
                        and attempt < self.max_retries
                    ):
                        logger.warning(
                            "Meta API temporary error %d on attempt %d. Retrying in %.2fs",
                            response.status_code,
                            attempt,
                            backoff,
                        )
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue

                    logger.error("Meta API error %d: %s", response.status_code, response.text)
                    return False
                except (httpx.ConnectError, httpx.TimeoutException) as exc:
                    if attempt < self.max_retries:
                        logger.warning("Network error on attempt %d: %s. Retrying...", attempt, exc)
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    logger.error("Meta API connection failed after %d attempts", self.max_retries)
                    return False
            return False
        finally:
            if should_close:
                await client.aclose()

    async def send_text(self, to_phone: str, body: str) -> bool:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }
        return await self._post_with_retry(payload)

    async def send_interactive_buttons(
        self, to_phone: str, body: str, buttons: list[dict[str, str]]
    ) -> bool:
        meta_buttons = [
            {
                "type": "reply",
                "reply": {
                    "id": b["id"],
                    "title": b["title"][:20],  # Meta limit: 20 chars per button title
                },
            }
            for b in buttons[:3]  # Meta limit: max 3 quick-reply buttons
        ]

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {"buttons": meta_buttons},
            },
        }
        return await self._post_with_retry(payload)

    async def send_document(
        self, to_phone: str, document_url: str, filename: str, caption: str | None = None
    ) -> bool:
        doc_payload: dict[str, Any] = {
            "link": document_url,
            "filename": filename,
        }
        if caption:
            doc_payload["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "document",
            "document": doc_payload,
        }
        return await self._post_with_retry(payload)
