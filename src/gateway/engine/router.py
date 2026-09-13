import re
from enum import Enum


class Intent(str, Enum):
    MENU = "MENU"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"
    ORDER_QUERY = "ORDER_QUERY"
    RETURN_QUERY = "RETURN_QUERY"
    UNKNOWN = "UNKNOWN"


class IntentRouter:
    """Fast deterministic intent router for common customer actions and quick-reply payloads."""

    def __init__(self) -> None:
        self._order_pattern = re.compile(
            r"(?:#?\s*(?:ORD|ORDER)[\s-]*#?(\d+))|(?:#(\d{4,}))",
            re.IGNORECASE,
        )

    def route(self, text: str, interactive_id: str | None = None) -> Intent:
        # Check quick-reply button identifier first
        if interactive_id:
            clean_id = interactive_id.lower()
            if "human" in clean_id or "agent" in clean_id:
                return Intent.HUMAN_ESCALATION
            if "menu" in clean_id or "options" in clean_id:
                return Intent.MENU
            if "track" in clean_id or "order" in clean_id:
                return Intent.ORDER_QUERY
            if "return" in clean_id or "refund" in clean_id:
                return Intent.RETURN_QUERY

        clean_text = text.strip().lower()

        # Human escalation check
        escalation_keywords = [
            "human",
            "agent",
            "representative",
            "manager",
            "speak to someone",
            "talk to someone",
            "real person",
            "live person",
        ]
        if any(keyword in clean_text for keyword in escalation_keywords):
            return Intent.HUMAN_ESCALATION

        # Menu and navigation check
        menu_keywords = ["menu", "help", "options", "start"]
        if clean_text in menu_keywords or any(clean_text.startswith(k) for k in menu_keywords):
            return Intent.MENU

        # Order lookup check
        order_keywords = ["order", "track", "tracking", "package", "where is", "shipping", "arrive"]
        if self._order_pattern.search(text) or any(
            keyword in clean_text for keyword in order_keywords
        ):
            return Intent.ORDER_QUERY

        # Return / refund check
        return_keywords = ["return", "refund", "exchange", "defective", "broken"]
        if any(keyword in clean_text for keyword in return_keywords):
            return Intent.RETURN_QUERY

        return Intent.UNKNOWN
