import pytest
from pydantic import ValidationError

from gateway.models.domain import (
    InboundMessageEvent,
    OrderRecord,
    OrderStatus,
    SessionRecord,
    SessionStatus,
)
from gateway.models.events import EscalationEventPayload
from gateway.models.tools import (
    CheckReturnEligibilityArgs,
    EscalateToHumanArgs,
    LookupOrderArgs,
)
from gateway.models.webhook import (
    MetaWebhookPayload,
    WhatsAppMessageType,
)


def test_meta_webhook_text_payload_parsing() -> None:
    raw_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1000123456789",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550001111",
                                "phone_number_id": "1000123456789",
                            },
                            "contacts": [
                                {"profile": {"name": "Alex Smith"}, "wa_id": "15559876543"}
                            ],
                            "messages": [
                                {
                                    "from": "15559876543",
                                    "id": "wamid.HBgLMTU1NTk4NzY1NDMVAgARGBI1QzYwODk4Q0YyNTgzMzhGAA==",
                                    "timestamp": "1725900000",
                                    "type": "text",
                                    "text": {"body": "Where is my order #ORD-1001?"},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    parsed = MetaWebhookPayload.model_validate(raw_payload)
    assert parsed.object == "whatsapp_business_account"
    assert len(parsed.entry) == 1
    assert len(parsed.entry[0].changes) == 1

    msg = parsed.entry[0].changes[0].value.messages[0]
    assert msg.from_number == "15559876543"
    assert msg.id.startswith("wamid.")
    assert msg.type == WhatsAppMessageType.TEXT
    assert msg.text is not None
    assert msg.text.body == "Where is my order #ORD-1001?"


def test_meta_webhook_interactive_payload_parsing() -> None:
    raw_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1000123456789",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [
                                {
                                    "from": "15559876543",
                                    "id": "wamid.HBgLMTU1NTk4NzY1NDMVAgARGBI1QzYwODk4Q0YyNTgzMzhGAA==",
                                    "timestamp": "1725900000",
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": "btn_track_order",
                                            "title": "Track Order",
                                        },
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    parsed = MetaWebhookPayload.model_validate(raw_payload)
    msg = parsed.entry[0].changes[0].value.messages[0]
    assert msg.type == WhatsAppMessageType.INTERACTIVE
    assert msg.interactive is not None
    assert msg.interactive.button_reply is not None
    assert msg.interactive.button_reply.id == "btn_track_order"
    assert msg.interactive.button_reply.title == "Track Order"


def test_meta_webhook_validation_failure() -> None:
    invalid_payload = {"object": "facebook_page"}
    with pytest.raises(ValidationError):
        MetaWebhookPayload.model_validate(invalid_payload)


def test_inbound_message_event() -> None:
    event = InboundMessageEvent(
        wamid="wamid.12345",
        sender_phone="15559876543",
        body="Track order #ORD-1001",
        interactive_id="btn_track_order",
        timestamp="1725900000",
    )
    assert event.wamid == "wamid.12345"
    assert event.interactive_id == "btn_track_order"


def test_order_record_and_status() -> None:
    order = OrderRecord(
        order_id="ORD-1001",
        customer_phone="15559876543",
        status=OrderStatus.SHIPPED,
        carrier="FedEx",
        tracking_number="TRK-987654",
        estimated_delivery="2026-09-15",
        items=["Wireless Noise-Canceling Headphones"],
        total_amount_usd=149.99,
        order_date="2026-09-08",
    )
    assert order.status == OrderStatus.SHIPPED
    assert order.total_amount_usd == 149.99
    assert len(order.items) == 1


def test_session_record_state_defaults() -> None:
    session = SessionRecord(
        phone_number="15559876543",
        last_interaction_ts=1725900000.0,
    )
    assert session.status == SessionStatus.ACTIVE_BOT
    assert session.transcript == []
    assert session.escalation_reason is None


def test_tool_schemas() -> None:
    lookup = LookupOrderArgs(order_id="ORD-1001")
    assert lookup.order_id == "ORD-1001"

    ret = CheckReturnEligibilityArgs(order_id="ORD-1001", reason="Wrong item received")
    assert ret.reason == "Wrong item received"

    esc = EscalateToHumanArgs(reason="Customer requested live human agent")
    assert esc.reason == "Customer requested live human agent"


def test_escalation_event_payload() -> None:
    payload = EscalationEventPayload(
        customer_phone="15559876543",
        reason="Frustrated customer requested manager",
        timestamp="2026-09-10T01:00:00Z",
        conversation_snippet=[
            {"role": "user", "message": "My item is broken"},
            {"role": "assistant", "message": "I understand, let me connect you to a specialist"},
        ],
    )
    assert payload.event_type == "ticket.escalated"
    assert len(payload.conversation_snippet) == 2
