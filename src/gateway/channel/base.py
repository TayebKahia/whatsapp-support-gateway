from typing import Protocol


class WhatsAppChannelPort(Protocol):
    """Port for dispatching outbound messages to the WhatsApp channel."""

    async def send_text(self, to_phone: str, body: str) -> bool:
        """Send a standard text message to the recipient's phone number."""
        ...

    async def send_interactive_buttons(
        self, to_phone: str, body: str, buttons: list[dict[str, str]]
    ) -> bool:
        """
        Send an interactive quick-reply button menu.

        buttons format: [{"id": "btn_1", "title": "Option 1"}, ...]
        """
        ...

    async def send_document(
        self, to_phone: str, document_url: str, filename: str, caption: str | None = None
    ) -> bool:
        """
        Send a media document (e.g. PDF shipping label or invoice).
        """
        ...
