from gateway.models.domain import OrderStatus
from gateway.repository.order import InMemoryOrderRepository


def test_get_order_existing() -> None:
    repo = InMemoryOrderRepository()
    order = repo.get_order("ORD-1001")

    assert order is not None
    assert order.order_id == "ORD-1001"
    assert order.status == OrderStatus.SHIPPED
    assert order.carrier == "FedEx"
    assert order.tracking_number == "TRK-987654"


def test_get_order_with_hash_prefix() -> None:
    repo = InMemoryOrderRepository()
    # Should strip # prefix gracefully
    order = repo.get_order("#ORD-1001")

    assert order is not None
    assert order.order_id == "ORD-1001"


def test_get_order_flexible_formats() -> None:
    repo = InMemoryOrderRepository()
    # "ord 1001", "order 1001", "1001", "ORD 1001"
    assert repo.get_order("ord 1001") is not None
    assert repo.get_order("order 1001") is not None
    assert repo.get_order("1001") is not None
    assert repo.get_order("ORD 1002") is not None
    assert repo.get_order("ORDER #1003") is not None


def test_get_order_not_found() -> None:
    repo = InMemoryOrderRepository()
    assert repo.get_order("ORD-NONEXISTENT") is None


def test_evaluate_return_delivered_eligible() -> None:
    repo = InMemoryOrderRepository()
    result = repo.evaluate_return("ORD-1003", reason="Item defective")

    assert result["eligible"] is True
    assert "instructions" in result
    assert "label" in result["instructions"].lower()


def test_evaluate_return_in_transit_ineligible() -> None:
    repo = InMemoryOrderRepository()
    result = repo.evaluate_return("ORD-1001", reason="Changed mind")

    assert result["eligible"] is False
    assert "transit" in result["reason"].lower()
