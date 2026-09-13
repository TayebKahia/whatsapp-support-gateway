from enum import Enum

from pydantic import BaseModel, Field


class InboundMessageEvent(BaseModel):
    """Normalized internal representation of an inbound WhatsApp message."""

    wamid: str = Field(description="Unique message ID for idempotency")
    sender_phone: str = Field(description="E.164 phone number of user")
    body: str = Field(description="Extracted message text or button payload")
    interactive_id: str | None = Field(default=None, description="Button ID if user clicked a menu")
    timestamp: str


class SessionStatus(str, Enum):
    ACTIVE_BOT = "ACTIVE_BOT"
    ESCALATED_HUMAN = "ESCALATED_HUMAN"
    CLOSED = "CLOSED"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderRecord(BaseModel):
    order_id: str
    customer_phone: str
    status: OrderStatus
    carrier: str | None = None
    tracking_number: str | None = None
    estimated_delivery: str | None = None
    items: list[str] = Field(default_factory=list)
    total_amount_usd: float
    order_date: str


class InteractiveButton(BaseModel):
    id: str = Field(description="Unique action payload identifier, e.g. btn_track")
    title: str = Field(description="Button label text, max 20 characters")


class SessionRecord(BaseModel):
    phone_number: str
    status: SessionStatus = SessionStatus.ACTIVE_BOT
    transcript: list[dict[str, str]] = Field(default_factory=list)
    last_interaction_ts: float
    escalation_reason: str | None = None
    last_referenced_order_id: str | None = None
    pending_verification_order_id: str | None = None
    verified_order_ids: list[str] = Field(default_factory=list)
