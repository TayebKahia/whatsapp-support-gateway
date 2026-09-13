from typing import Any


class MockWhatsAppAdapter:
    """In-memory mock adapter for offline testing and interactive CLI simulation."""

    def __init__(self) -> None:
        self.sent_messages: list[dict[str, Any]] = []

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

    def clear(self) -> None:
        self.sent_messages.clear()
