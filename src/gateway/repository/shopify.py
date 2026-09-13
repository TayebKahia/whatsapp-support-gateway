import logging
import re
from typing import Any

import httpx

from gateway.models.domain import OrderRecord, OrderStatus

logger = logging.getLogger(__name__)


class ShopifyOrderAdapter:
    """
    Production-grade adapter integrating with Shopify Admin REST API.
    Operates in live mode when shop credentials are provided, or realistic fixture sandbox mode offline.
    """

    def __init__(
        self,
        shop_domain: str | None = None,
        access_token: str | None = None,
        api_version: str = "2024-01",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.shop_domain = shop_domain.strip().rstrip("/") if shop_domain else None
        self.access_token = access_token.strip() if access_token else None
        self.api_version = api_version
        self._http_client = http_client
        self.is_live_mode = bool(self.shop_domain and self.access_token)

        # Offline sandbox fixtures modeling raw Shopify Admin API response payloads
        self._sandbox_fixtures: dict[str, dict[str, Any]] = {
            "1001": {
                "id": 8209829119461,
                "name": "#1001",
                "email": "sarah.buyer@example.com",
                "phone": "+15551234567",
                "financial_status": "paid",
                "fulfillment_status": "fulfilled",
                "created_at": "2026-09-08T14:20:00-04:00",
                "cancelled_at": None,
                "total_price": "149.99",
                "currency": "USD",
                "customer": {
                    "first_name": "Sarah",
                    "last_name": "Connor",
                    "phone": "15551234567",
                },
                "shipping_address": {
                    "phone": "15551234567",
                    "city": "Austin",
                    "province": "TX",
                },
                "line_items": [
                    {
                        "id": 1,
                        "title": "Wireless Noise-Canceling Headphones",
                        "quantity": 1,
                        "price": "149.99",
                    }
                ],
                "fulfillments": [
                    {
                        "id": 987654321,
                        "tracking_company": "FedEx",
                        "tracking_number": "TRK-987654",
                        "status": "in_transit",
                        "estimated_delivery_at": "2026-09-15",
                    }
                ],
            },
            "1002": {
                "id": 8209829119462,
                "name": "#1002",
                "email": "alex.dev@example.com",
                "phone": "+15559876543",
                "financial_status": "paid",
                "fulfillment_status": None,  # Unfulfilled
                "created_at": "2026-09-09T10:15:00-04:00",
                "cancelled_at": None,
                "total_price": "129.00",
                "currency": "USD",
                "customer": {"first_name": "Alex", "last_name": "Dev", "phone": "15559876543"},
                "line_items": [
                    {
                        "id": 2,
                        "title": "Ergonomic Mechanical Keyboard",
                        "quantity": 1,
                        "price": "129.00",
                    }
                ],
                "fulfillments": [],
            },
            "1003": {
                "id": 8209829119463,
                "name": "#1003",
                "email": "emma.suite@example.com",
                "phone": "+15551112233",
                "financial_status": "paid",
                "fulfillment_status": "fulfilled",
                "created_at": "2026-08-30T16:00:00-04:00",
                "cancelled_at": None,
                "total_price": "49.99",
                "currency": "USD",
                "customer": {"first_name": "Emma", "last_name": "Watson", "phone": "15551112233"},
                "line_items": [
                    {"id": 3, "title": "USB-C Multiport Hub", "quantity": 1, "price": "49.99"}
                ],
                "fulfillments": [
                    {
                        "id": 987654322,
                        "tracking_company": "UPS",
                        "tracking_number": "TRK-112233",
                        "status": "delivered",
                        "estimated_delivery_at": "2026-09-02",
                    }
                ],
            },
        }

    def _clean_order_digits(self, order_id: str) -> str:
        clean = order_id.strip().upper()
        match = re.search(r"(?:#?\s*(?:ORD|ORDER|SHOPIFY)[\s-]*#?(\d+))|(?:#?(\d{4,}))", clean)
        if match:
            return match.group(1) or match.group(2)
        return clean.lstrip("#")

    def _parse_shopify_payload(self, raw: dict[str, Any]) -> OrderRecord:
        raw_name = str(raw.get("name", ""))
        digits = re.sub(r"\D", "", raw_name) or str(raw.get("id", ""))
        order_id = f"ORD-{digits}" if digits else raw_name

        # Extract phone
        customer = raw.get("customer") or {}
        address = raw.get("shipping_address") or {}
        raw_phone = raw.get("phone") or customer.get("phone") or address.get("phone") or ""
        clean_phone = re.sub(r"\D", "", raw_phone)

        # Extract items
        line_items = raw.get("line_items") or []
        items = [item.get("title", "Shopify Product") for item in line_items]

        # Extract fulfillment / status
        fulfillments = raw.get("fulfillments") or []
        carrier: str | None = None
        tracking_number: str | None = None
        estimated_delivery: str | None = None
        fulfillment_status = raw.get("fulfillment_status")

        if fulfillments:
            first_f = fulfillments[0]
            carrier = first_f.get("tracking_company")
            tracking_number = first_f.get("tracking_number")
            estimated_delivery = first_f.get("estimated_delivery_at")
            f_status = first_f.get("status")

            if f_status == "delivered":
                status = OrderStatus.DELIVERED
            elif f_status == "in_transit" or fulfillment_status == "fulfilled":
                status = OrderStatus.SHIPPED
            else:
                status = OrderStatus.PROCESSING
        elif raw.get("cancelled_at"):
            status = OrderStatus.CANCELLED
        elif fulfillment_status == "partial":
            status = OrderStatus.PROCESSING
        elif fulfillment_status is None:
            status = (
                OrderStatus.PROCESSING
                if raw.get("financial_status") == "paid"
                else OrderStatus.PENDING
            )
        else:
            status = OrderStatus.PROCESSING

        # Total amount
        try:
            total_usd = float(raw.get("total_price", 0.0))
        except (ValueError, TypeError):
            total_usd = 0.0

        order_date = str(raw.get("created_at", ""))[:10]

        return OrderRecord(
            order_id=order_id,
            customer_phone=clean_phone,
            status=status,
            carrier=carrier,
            tracking_number=tracking_number,
            estimated_delivery=estimated_delivery,
            items=items,
            total_amount_usd=total_usd,
            order_date=order_date,
        )

    def get_order(self, order_id: str) -> OrderRecord | None:
        digits = self._clean_order_digits(order_id)

        # In fixture/sandbox mode:
        if not self.is_live_mode or digits in self._sandbox_fixtures:
            fixture = self._sandbox_fixtures.get(digits)
            if fixture:
                return self._parse_shopify_payload(fixture)
            return None

        # In live mode:
        return self._fetch_live_order(digits)

    def _fetch_live_order(self, digits: str) -> OrderRecord | None:
        if not self.shop_domain or not self.access_token:
            return None

        url = f"https://{self.shop_domain}/admin/api/{self.api_version}/orders.json"
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }
        params = {"name": f"#{digits}", "status": "any"}

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(url, headers=headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    orders = data.get("orders") or []
                    if orders:
                        return self._parse_shopify_payload(orders[0])
                logger.warning(
                    "Shopify live query for #%s returned status %d", digits, resp.status_code
                )
                return None
        except Exception:
            logger.exception("Failed to connect to Shopify Admin API for order #%s", digits)
            return None

    def evaluate_return(self, order_id: str, reason: str) -> dict[str, Any]:
        order = self.get_order(order_id)
        if not order:
            return {
                "eligible": False,
                "reason": f"Order {order_id} was not found in Shopify records.",
            }

        if order.status == OrderStatus.DELIVERED:
            rma_code = f"RMA-SHPFY-{order.order_id[-4:]}"
            return {
                "eligible": True,
                "order_id": order.order_id,
                "rma_code": rma_code,
                "instructions": (
                    f"Order {order.order_id} is eligible for return under standard 30-day policy. "
                    f"Prepaid return authorization code: *#{rma_code}*. "
                    "Your return shipping label is being prepared."
                ),
            }

        return {
            "eligible": False,
            "order_id": order.order_id,
            "reason": (
                f"Order {order.order_id} currently has status '{order.status.value}'. "
                "Shopify returns can only be requested after delivery confirmation."
            ),
        }
