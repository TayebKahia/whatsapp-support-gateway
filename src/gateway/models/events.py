from typing import Literal

from pydantic import BaseModel, Field


class EscalationEventPayload(BaseModel):
    """Event payload emitted to external automations (e.g. n8n / Zapier) upon human escalation."""

    event_type: Literal["ticket.escalated"] = "ticket.escalated"
    customer_phone: str
    reason: str
    timestamp: str
    conversation_snippet: list[dict[str, str]] = Field(default_factory=list)
