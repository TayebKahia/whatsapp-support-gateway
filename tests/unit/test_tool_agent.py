import pytest

from gateway.engine.agent import BoundedToolAgent
from gateway.repository.order import InMemoryOrderRepository


@pytest.mark.asyncio
async def test_tool_agent_lookup_order_success() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    response = await agent.handle_order_query("Where is my order #ORD-1001?")
    assert "ORD-1001" in response
    assert "SHIPPED" in response
    assert "FedEx" in response
    assert "TRK-987654" in response


@pytest.mark.asyncio
async def test_tool_agent_lookup_order_missing_id() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    response = await agent.handle_order_query("Can you track my order?")
    assert "order number" in response.lower()


@pytest.mark.asyncio
async def test_tool_agent_lookup_order_not_found() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    response = await agent.handle_order_query("Where is ORD-9999?")
    assert "could not find" in response.lower() or "not found" in response.lower()


@pytest.mark.asyncio
async def test_tool_agent_return_eligibility() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    response = await agent.handle_return_query(
        "I want to return order ORD-1003 because it's defective"
    )
    assert "eligible" in response.lower()
    assert "prepaid return label" in response.lower()


@pytest.mark.asyncio
async def test_tool_agent_lookup_order_flexible_phrasing() -> None:
    order_repo = InMemoryOrderRepository()
    agent = BoundedToolAgent(order_repo=order_repo)

    # ord 1001 (space, lowercase)
    resp1 = await agent.handle_order_query("Where is ord 1001?")
    assert "ORD-1001" in resp1
    assert "SHIPPED" in resp1

    # order 1002 (word order, space)
    resp2 = await agent.handle_order_query("Can you check order 1002 please")
    assert "ORD-1002" in resp2
    assert "PROCESSING" in resp2

    # #1001 (just hash and digits)
    resp3 = await agent.handle_order_query("What about #1001")
    assert "ORD-1001" in resp3
    assert "SHIPPED" in resp3

    # return with ord 1003
    resp4 = await agent.handle_return_query("Return ord 1003")
    assert "ORD-1003" in resp4
    assert "eligible" in resp4.lower()
