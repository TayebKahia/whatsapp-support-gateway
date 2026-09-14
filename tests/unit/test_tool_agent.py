import pytest

from gateway.engine.agent import BoundedToolAgent
from gateway.repository.order import InMemoryOrderRepository


@pytest.mark.asyncio
async def test_tool_agent_lookup_order_success() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    response, buttons = await agent.handle_order_query("Where is my order #ORD-1001?")
    assert "ORD-1001" in response
    assert "SHIPPED" in response
    assert "FedEx" in response
    assert "TRK-987654" in response
    assert buttons is not None


@pytest.mark.asyncio
async def test_tool_agent_lookup_order_missing_id() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    response, buttons = await agent.handle_order_query("Can you track my order?")
    assert "order number" in response.lower()
    assert buttons is None


@pytest.mark.asyncio
async def test_tool_agent_lookup_order_not_found() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    response, buttons = await agent.handle_order_query("Where is ORD-9999?")
    assert "could not find" in response.lower() or "not found" in response.lower()
    assert buttons is None


@pytest.mark.asyncio
async def test_tool_agent_return_eligibility() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    response, buttons, document = await agent.handle_return_query(
        "I want to return order ORD-1003 because it's defective"
    )
    assert "eligible" in response.lower()
    assert "prepaid return label" in response.lower()
    assert buttons is not None
    assert document is not None
    assert "ORD-1003.pdf" in document["document_url"]


@pytest.mark.asyncio
async def test_tool_agent_lookup_order_flexible_phrasing() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    # ord 1001 (space, lowercase)
    resp1, _ = await agent.handle_order_query("Where is ord 1001?")
    assert "ORD-1001" in resp1
    assert "SHIPPED" in resp1

    # order 1002 (word order, space)
    resp2, _ = await agent.handle_order_query("Can you check order 1002 please")
    assert "ORD-1002" in resp2
    assert "PROCESSING" in resp2

    # #1001 (just hash and digits)
    resp3, _ = await agent.handle_order_query("What about #1001")
    assert "ORD-1001" in resp3
    assert "SHIPPED" in resp3

    # return with ord 1003
    resp4, _, _ = await agent.handle_return_query("Return ord 1003")
    assert "ORD-1003" in resp4
    assert "eligible" in resp4.lower()


@pytest.mark.asyncio
async def test_tool_agent_phone_lookup_single_order() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    reply, buttons = await agent.handle_order_query(
        "Track Order",
        sender_phone="15551234567",
    )
    assert "ORD-1001" in reply
    assert "SHIPPED" in reply
    assert buttons is not None


@pytest.mark.asyncio
async def test_tool_agent_phone_lookup_multiple_orders() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    # 15557778899 has 2 orders: ORD-1004 and ORD-1005
    reply, buttons = await agent.handle_order_query(
        "Track Order",
        sender_phone="15557778899",
    )
    assert "2 packages" in reply
    assert "ORD-1004" in reply
    assert "ORD-1005" in reply
    assert buttons is not None
    assert len(buttons) == 2
    assert any(b["id"] == "track_ORD-1004" for b in buttons)
    assert any(b["id"] == "track_ORD-1005" for b in buttons)


@pytest.mark.asyncio
async def test_tool_agent_phone_lookup_zero_orders() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    reply, buttons = await agent.handle_order_query(
        "Track Order",
        sender_phone="15550000000",
    )
    assert "could not find any active orders" in reply.lower()
    assert "order number" in reply.lower()
    assert buttons is None


@pytest.mark.asyncio
async def test_tool_agent_phone_lookup_return_multiple_orders() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    reply, buttons, doc = await agent.handle_return_query(
        "Return / Refund",
        sender_phone="15557778899",
    )
    assert "2 orders" in reply
    assert "ORD-1004" in reply
    assert "ORD-1005" in reply
    assert buttons is not None
    assert len(buttons) == 2
    assert doc is None
