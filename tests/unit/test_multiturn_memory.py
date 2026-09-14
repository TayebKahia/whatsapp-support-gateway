import pytest

from gateway.engine.agent import BoundedToolAgent
from gateway.models.domain import SessionRecord
from gateway.repository.order import InMemoryOrderRepository


@pytest.mark.asyncio
async def test_multiturn_memory_return_followup() -> None:
    repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=repo)
    # ORD-1003 customer_phone is "15551112233"
    session = SessionRecord(phone_number="15551112233", last_interaction_ts=1000.0)

    # Turn 1: Query order 1003
    reply1, _ = await agent.handle_order_query(
        query="Status for #ORD-1003",
        sender_phone="15551112233",
        session=session,
    )
    assert "ORD-1003" in reply1
    assert session.last_referenced_order_id == "ORD-1003"

    # Turn 2: Follow-up using pronoun "it" without repeating order number
    reply2, buttons2, document2 = await agent.handle_return_query(
        query="Can I return it please?",
        sender_phone="15551112233",
        session=session,
    )
    assert "ORD-1003" in reply2
    assert "eligible" in reply2.lower()
    assert buttons2 is not None
    assert document2 is not None
    assert "ORD-1003.pdf" in document2["document_url"]


@pytest.mark.asyncio
async def test_multiturn_memory_tracking_followup() -> None:
    repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=repo)
    session = SessionRecord(
        phone_number="15559876543",
        last_interaction_ts=1000.0,
        last_referenced_order_id="ORD-1002",
        verified_order_ids=["ORD-1002"],
    )

    # Follow-up: "When will it arrive?"
    reply, _ = await agent.handle_order_query(
        query="When will it arrive?",
        sender_phone="15559876543",
        session=session,
    )
    assert "ORD-1002" in reply
    assert "PROCESSING" in reply


@pytest.mark.asyncio
async def test_multiturn_memory_no_context_prompts_for_id() -> None:
    repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=repo)
    # Customer with no orders on file asks ambiguous question
    session = SessionRecord(phone_number="15550000000", last_interaction_ts=1000.0)

    reply, _ = await agent.handle_order_query(
        query="Where is it?",
        sender_phone="15550000000",
        session=session,
    )
    assert "order number" in reply.lower()
