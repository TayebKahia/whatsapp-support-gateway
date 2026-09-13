import pytest

from gateway.engine.agent import BoundedToolAgent
from gateway.models.domain import SessionRecord
from gateway.repository.order import InMemoryOrderRepository


@pytest.mark.asyncio
async def test_order_access_matching_phone_auto_verified() -> None:
    repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=repo)
    session = SessionRecord(phone_number="15551234567", last_interaction_ts=1000.0)

    # ORD-1001 customer_phone is "15551234567"
    reply, buttons = await agent.handle_order_query(
        query="Where is ORD-1001?",
        sender_phone="15551234567",
        session=session,
    )

    assert "ORD-1001" in reply
    assert "SHIPPED" in reply
    assert session.last_referenced_order_id == "ORD-1001"
    assert "ORD-1001" in session.verified_order_ids
    assert session.pending_verification_order_id is None
    assert buttons is not None
    assert any(b["id"] == "btn_return" for b in buttons)


@pytest.mark.asyncio
async def test_order_access_mismatched_phone_requires_verification() -> None:
    repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=repo)
    # Caller phone is 15559999999, but ORD-1001 belongs to 15551234567
    session = SessionRecord(phone_number="15559999999", last_interaction_ts=1000.0)

    reply, _ = await agent.handle_order_query(
        query="Where is ORD-1001?",
        sender_phone="15559999999",
        session=session,
    )

    # Order details must NOT be disclosed
    assert "SHIPPED" not in reply
    assert "TRK-987654" not in reply
    assert "Security Verification" in reply or "verify" in reply.lower()
    assert session.pending_verification_order_id == "ORD-1001"


@pytest.mark.asyncio
async def test_verify_order_ownership_success_with_last_4_digits() -> None:
    repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=repo)
    session = SessionRecord(
        phone_number="15559999999",
        last_interaction_ts=1000.0,
        pending_verification_order_id="ORD-1001",
    )

    # ORD-1001 customer_phone is "15551234567", so last 4 digits are "4567"
    reply, buttons, verified = await agent.verify_order_ownership("4567", session)

    assert verified is True
    assert "ORD-1001" in reply
    assert "SHIPPED" in reply
    assert session.pending_verification_order_id is None
    assert "ORD-1001" in session.verified_order_ids
    assert session.last_referenced_order_id == "ORD-1001"
    assert buttons is not None


@pytest.mark.asyncio
async def test_verify_order_ownership_failure_with_wrong_digits() -> None:
    repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=repo)
    session = SessionRecord(
        phone_number="15559999999",
        last_interaction_ts=1000.0,
        pending_verification_order_id="ORD-1001",
    )

    reply, _, verified = await agent.verify_order_ownership("0000", session)

    assert verified is False
    assert "SHIPPED" not in reply
    assert "failed" in reply.lower() or "incorrect" in reply.lower()
    assert session.pending_verification_order_id == "ORD-1001"
