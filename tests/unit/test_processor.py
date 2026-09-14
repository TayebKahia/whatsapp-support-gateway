import pytest

from gateway.channel.mock import MockWhatsAppAdapter
from gateway.engine.processor import MessageProcessor
from gateway.models.domain import InboundMessageEvent, SessionStatus
from gateway.repository.order import InMemoryOrderRepository
from gateway.repository.session import InMemorySessionStore


@pytest.mark.asyncio
async def test_processor_menu_flow() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    processor = MessageProcessor(
        channel=channel,
        order_repo=order_repo,
        session_store=session_store,
    )

    event = InboundMessageEvent(
        wamid="wamid.P001",
        sender_phone="15551234567",
        body="menu",
        timestamp="1725900000",
    )

    await processor.process_event(event)

    assert len(channel.sent_messages) == 1
    assert channel.sent_messages[0]["to"] == "15551234567"
    assert channel.sent_messages[0]["type"] == "interactive"


@pytest.mark.asyncio
async def test_processor_order_query_flow() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    processor = MessageProcessor(
        channel=channel,
        order_repo=order_repo,
        session_store=session_store,
    )

    event = InboundMessageEvent(
        wamid="wamid.P002",
        sender_phone="15551234567",
        body="Where is order #ORD-1001?",
        timestamp="1725900000",
    )

    await processor.process_event(event)

    assert len(channel.sent_messages) == 1
    reply = channel.sent_messages[0]["body"]
    assert "ORD-1001" in reply
    assert "FedEx" in reply


@pytest.mark.asyncio
async def test_processor_human_escalation_and_muting_flow() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    processor = MessageProcessor(
        channel=channel,
        order_repo=order_repo,
        session_store=session_store,
    )
    phone = "15551234567"

    # Step 1: User asks for human agent
    event1 = InboundMessageEvent(
        wamid="wamid.P003",
        sender_phone=phone,
        body="I need to speak to a human representative please",
        timestamp="1725900000",
    )
    await processor.process_event(event1)

    # Initial escalation response sent to user
    assert len(channel.sent_messages) == 1
    assert (
        "human" in channel.sent_messages[0]["body"].lower()
        or "agent" in channel.sent_messages[0]["body"].lower()
    )

    # Session is now ESCALATED_HUMAN
    session = session_store.get_session(phone)
    assert session.status == SessionStatus.ESCALATED_HUMAN

    # Step 2: Customer sends another message while escalated
    channel.clear()
    event2 = InboundMessageEvent(
        wamid="wamid.P004",
        sender_phone=phone,
        body="Are you still there? My receipt is #9988",
        timestamp="1725900100",
    )
    await processor.process_event(event2)

    # ZERO messages dispatched because bot is muted!
    assert len(channel.sent_messages) == 0

    # But transcript must contain the message!
    session = session_store.get_session(phone)
    transcript_messages = [t["message"] for t in session.transcript]
    assert "Are you still there? My receipt is #9988" in transcript_messages


@pytest.mark.asyncio
async def test_processor_pending_verification_switch_order_does_not_trap() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    processor = MessageProcessor(
        channel=channel,
        order_repo=order_repo,
        session_store=session_store,
    )
    phone = "15551234567"

    # Set up pending verification for ORD-1002 (which belongs to a different phone)
    session = session_store.get_session(phone)
    session.pending_verification_order_id = "ORD-1002"
    session_store.save_session(session)

    # User asks about ORD-1001 instead of providing digits
    event = InboundMessageEvent(
        wamid="wamid.SW001",
        sender_phone=phone,
        body="Where is ord 1001?",
        timestamp="1725900000",
    )
    await processor.process_event(event)

    # Must NOT fail verification; must resolve ORD-1001!
    assert len(channel.sent_messages) == 1
    reply = channel.sent_messages[0]["body"]
    assert "ORD-1001" in reply
    assert "SHIPPED" in reply
    assert "Verification failed" not in reply

    # Pending verification should be cleared
    updated_session = session_store.get_session(phone)
    assert updated_session.pending_verification_order_id is None


@pytest.mark.asyncio
async def test_processor_pending_verification_navigation_escape() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    processor = MessageProcessor(
        channel=channel,
        order_repo=order_repo,
        session_store=session_store,
    )
    phone = "15551234567"

    # Set up pending verification for ORD-1002
    session = session_store.get_session(phone)
    session.pending_verification_order_id = "ORD-1002"
    session_store.save_session(session)

    # User clicks generic Track Order button
    event = InboundMessageEvent(
        wamid="wamid.ESC001",
        sender_phone=phone,
        body="Track Order",
        interactive_id="btn_track",
        timestamp="1725900000",
    )
    await processor.process_event(event)

    # Must NOT fail verification; must look up user's order ORD-1001!
    assert len(channel.sent_messages) == 1
    reply = channel.sent_messages[0]["body"]
    assert "ORD-1001" in reply
    assert "Verification failed" not in reply


@pytest.mark.asyncio
async def test_processor_generic_track_phone_lookup() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()
    processor = MessageProcessor(
        channel=channel,
        order_repo=order_repo,
        session_store=session_store,
    )
    phone = "15551234567"

    # User simply clicks "Track Order" with no prior context or order ID
    event = InboundMessageEvent(
        wamid="wamid.TRK001",
        sender_phone=phone,
        body="Track Order",
        interactive_id="btn_track",
        timestamp="1725900000",
    )
    await processor.process_event(event)

    # Automatically finds ORD-1001 linked to 15551234567!
    assert len(channel.sent_messages) == 1
    reply = channel.sent_messages[0]["body"]
    assert "ORD-1001" in reply
    assert "FedEx" in reply
