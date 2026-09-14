import re
from typing import Any, Protocol

from gateway.models.domain import OrderRecord, OrderStatus


class OrderRepository(Protocol):
    """Port for accessing e-commerce order and fulfillment data."""

    def get_order(self, order_id: str) -> OrderRecord | None:
        """Lookup an order by its identifier (e.g. ORD-1001 or #ORD-1001)."""
        ...

    def get_orders_by_customer_phone(self, phone: str) -> list[OrderRecord]:
        """Lookup all orders belonging to a customer's phone number."""
        ...

    def evaluate_return(self, order_id: str, reason: str) -> dict[str, Any]:
        """Evaluate whether an order is eligible for return or refund."""
        ...


class InMemoryOrderRepository:
    """Pre-seeded repository implementing order operations for tests and local demo."""

    def __init__(self) -> None:
        self._orders: dict[str, OrderRecord] = {
            "ORD-1001": OrderRecord(
                order_id="ORD-1001",
                customer_phone="15551234567",
                status=OrderStatus.SHIPPED,
                carrier="FedEx",
                tracking_number="TRK-987654",
                estimated_delivery="2026-09-15",
                items=["Wireless Noise-Canceling Headphones"],
                total_amount_usd=149.99,
                order_date="2026-09-08",
            ),
            "ORD-1002": OrderRecord(
                order_id="ORD-1002",
                customer_phone="15559876543",
                status=OrderStatus.PROCESSING,
                carrier=None,
                tracking_number=None,
                estimated_delivery="2026-09-18",
                items=["Ergonomic Mechanical Keyboard"],
                total_amount_usd=129.00,
                order_date="2026-09-09",
            ),
            "ORD-1003": OrderRecord(
                order_id="ORD-1003",
                customer_phone="15551112233",
                status=OrderStatus.DELIVERED,
                carrier="UPS",
                tracking_number="TRK-112233",
                estimated_delivery="2026-09-02",
                items=["USB-C Multiport Hub"],
                total_amount_usd=49.99,
                order_date="2026-08-30",
            ),
            "ORD-1004": OrderRecord(
                order_id="ORD-1004",
                customer_phone="15557778899",
                status=OrderStatus.SHIPPED,
                carrier="DHL Express",
                tracking_number="TRK-778899",
                estimated_delivery="2026-09-16",
                items=["Smart Fitness Watch"],
                total_amount_usd=199.00,
                order_date="2026-09-10",
            ),
            "ORD-1005": OrderRecord(
                order_id="ORD-1005",
                customer_phone="15557778899",
                status=OrderStatus.DELIVERED,
                carrier="FedEx",
                tracking_number="TRK-556677",
                estimated_delivery="2026-09-05",
                items=["Bluetooth Soundbar"],
                total_amount_usd=89.50,
                order_date="2026-09-01",
            ),
        }

    def get_orders_by_customer_phone(self, phone: str) -> list[OrderRecord]:
        clean_target = re.sub(r"\D", "", phone)
        return [
            order
            for order in self._orders.values()
            if re.sub(r"\D", "", order.customer_phone) == clean_target
        ]

    def _clean_order_id(self, order_id: str) -> str:
        clean = order_id.strip().upper()
        match = re.search(r"(?:#?\s*(?:ORD|ORDER)[\s-]*#?(\d+))|(?:#?(\d{4,}))", clean)
        if match:
            digits = match.group(1) or match.group(2)
            return f"ORD-{digits}"
        return clean.lstrip("#")

    def get_order(self, order_id: str) -> OrderRecord | None:
        clean_id = self._clean_order_id(order_id)
        return self._orders.get(clean_id)

    def evaluate_return(self, order_id: str, reason: str) -> dict[str, Any]:
        clean_id = self._clean_order_id(order_id)
        order = self._orders.get(clean_id)

        if not order:
            return {"eligible": False, "reason": f"Order {order_id} was not found in our records."}

        if order.status == OrderStatus.DELIVERED:
            return {
                "eligible": True,
                "order_id": order.order_id,
                "instructions": (
                    f"Order {order.order_id} is eligible for return. Please pack the item and use "
                    f"prepaid return label #RET-{order.order_id[-4:]}. Drop it at any authorized drop-off point."
                ),
            }

        return {
            "eligible": False,
            "order_id": order.order_id,
            "reason": (
                f"Order {order.order_id} currently has status '{order.status.value}' and is still in transit. "
                "Returns can only be requested once the item has been delivered."
            ),
        }
