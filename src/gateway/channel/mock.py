from typing import Any


class MockWhatsAppAdapter:
    """In-memory mock adapter for offline testing and interactive CLI simulation."""

    def __init__(self) -> None:
        self.sent_messages: list[dict[str, Any]] = []
        self.read_wamids: list[str] = []

    async def send_text(self, to_phone: str, body: str) -> bool:
        self.sent_messages.append(
            {
                "to": to_phone,
                "type": "text",
                "body": body,
            }
        )
        return True

    async def send_interactive_buttons(
        self, to_phone: str, body: str, buttons: list[dict[str, str]]
    ) -> bool:
        self.sent_messages.append(
            {
                "to": to_phone,
                "type": "interactive",
                "body": body,
                "buttons": buttons,
            }
        )
        return True

    async def send_document(
        self, to_phone: str, document_url: str, filename: str, caption: str | None = None
    ) -> bool:
        self.sent_messages.append(
            {
                "to": to_phone,
                "type": "document",
                "document_url": document_url,
                "filename": filename,
                "caption": caption,
            }
        )
        return True

    async def mark_read(self, wamid: str) -> bool:
        self.read_wamids.append(wamid)
        return True

    def clear(self) -> None:
        self.sent_messages.clear()
        self.read_wamids.clear()
