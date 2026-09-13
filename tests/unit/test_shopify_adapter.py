from unittest.mock import MagicMock, patch

from gateway.models.domain import OrderStatus
from gateway.repository.shopify import ShopifyOrderAdapter


def test_shopify_adapter_fixture_order_fulfilled() -> None:
    adapter = ShopifyOrderAdapter()
    order = adapter.get_order("1001")

    assert order is not None
    assert order.order_id == "ORD-1001"
    assert order.status == OrderStatus.SHIPPED
    assert order.carrier == "FedEx"
    assert order.tracking_number == "TRK-987654"
    assert "Wireless Noise-Canceling Headphones" in order.items
    assert order.total_amount_usd == 149.99
    assert order.customer_phone == "15551234567"


def test_shopify_adapter_fixture_order_processing() -> None:
    adapter = ShopifyOrderAdapter()
    order = adapter.get_order("SHOPIFY-1002")

    assert order is not None
    assert order.order_id == "ORD-1002"
    assert order.status == OrderStatus.PROCESSING
    assert order.carrier is None
    assert order.tracking_number is None


def test_shopify_adapter_fixture_not_found() -> None:
    adapter = ShopifyOrderAdapter()
    assert adapter.get_order("9999") is None


def test_shopify_adapter_evaluate_return_eligible() -> None:
    adapter = ShopifyOrderAdapter()
    # 1003 is delivered
    result = adapter.evaluate_return("1003", reason="Damaged connector")

    assert result["eligible"] is True
    assert "RMA-SHPFY-1003" in result["rma_code"]
    assert "30-day" in result["instructions"].lower()


def test_shopify_adapter_evaluate_return_ineligible() -> None:
    adapter = ShopifyOrderAdapter()
    # 1001 is shipped/in transit
    result = adapter.evaluate_return("1001", reason="Changed mind")

    assert result["eligible"] is False
    assert "delivery confirmation" in result["reason"].lower()


def test_shopify_adapter_live_mode_query() -> None:
    adapter = ShopifyOrderAdapter(
        shop_domain="example.myshopify.com",
        access_token="shpat_test_token_secret",
    )
    assert adapter.is_live_mode is True

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "orders": [
            {
                "id": 999111,
                "name": "#7777",
                "phone": "+15557778899",
                "fulfillment_status": "fulfilled",
                "total_price": "89.50",
                "created_at": "2026-09-12T10:00:00Z",
                "customer": {"phone": "15557778899"},
                "line_items": [{"title": "Wireless Gaming Mouse"}],
                "fulfillments": [
                    {
                        "tracking_company": "DHL",
                        "tracking_number": "DHL-777888",
                        "status": "delivered",
                    }
                ],
            }
        ]
    }

    with patch("httpx.Client.get", return_value=mock_resp):
        order = adapter.get_order("7777")
        assert order is not None
        assert order.order_id == "ORD-7777"
        assert order.carrier == "DHL"
        assert order.tracking_number == "DHL-777888"
        assert order.status == OrderStatus.DELIVERED
        assert order.total_amount_usd == 89.50
