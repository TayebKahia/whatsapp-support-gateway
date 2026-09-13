import re

from gateway.models.tools import CheckReturnEligibilityArgs, LookupOrderArgs
from gateway.repository.order import OrderRepository


class BoundedToolAgent:
    """Bounded AI tool-calling agent enforcing typed schemas on all backend operations."""

    def __init__(self, order_repo: OrderRepository) -> None:
        self.order_repo = order_repo
        # Flexible pattern matching: ORD-1001, ord 1001, order 1001, order #1001, #1001
        self._order_pattern = re.compile(
            r"(?:#?\s*(?:ORD|ORDER)[\s-]*#?(\d+))|(?:#(\d{4,}))",
            re.IGNORECASE,
        )

    def extract_order_id(self, text: str) -> str | None:
        match = self._order_pattern.search(text)
        if match:
            digits = match.group(1) or match.group(2)
            return f"ORD-{digits}"
        return None

    async def handle_order_query(self, query: str) -> str:
        order_id = self.extract_order_id(query)
        if not order_id:
            return (
                "To check your shipment status, please reply with your order number "
                "(for example: *#ORD-1001*)."
            )

        args = LookupOrderArgs(order_id=order_id)
        order = self.order_repo.get_order(args.order_id)

        if not order:
            return (
                f"We could not find order *{args.order_id}* in our records. "
                "Please double-check the order number and try again."
            )

        carrier_str = order.carrier if order.carrier else "Preparing for dispatch"
        tracking_str = (
            order.tracking_number if order.tracking_number else "Will be assigned upon pickup"
        )
        eta_str = order.estimated_delivery if order.estimated_delivery else "To be determined"
        items_str = ", ".join(order.items) if order.items else "N/A"

        return (
            f"📦 *Order Status: #{order.order_id}*\n"
            f"• Status: *{order.status.value}*\n"
            f"• Carrier: {carrier_str}\n"
            f"• Tracking #: {tracking_str}\n"
            f"• Est. Delivery: {eta_str}\n"
            f"• Items: {items_str}"
        )

    async def handle_return_query(self, query: str) -> str:
        order_id = self.extract_order_id(query)
        if not order_id:
            return (
                "To assist with returns or refunds, please provide your order number "
                "(for example: *#ORD-1003*)."
            )

        args = CheckReturnEligibilityArgs(order_id=order_id, reason=query)
        result = self.order_repo.evaluate_return(args.order_id, reason=args.reason)

        if result["eligible"]:
            return f"✅ *Return Approved for #{args.order_id}*\n\n{result['instructions']}"

        return f"ℹ️ *Return Ineligible for #{args.order_id}*\n\n{result['reason']}"
