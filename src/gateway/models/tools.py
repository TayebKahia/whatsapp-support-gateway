from pydantic import BaseModel, Field


class LookupOrderArgs(BaseModel):
    """Arguments for querying order status by order ID."""

    order_id: str = Field(
        description="The order number extracted from the customer query (e.g. #ORD-1001 or ORD-1001)"
    )


class CheckReturnEligibilityArgs(BaseModel):
    """Arguments for checking if an order/item is eligible for refund or return."""

    order_id: str = Field(description="Order ID to evaluate for return")
    reason: str = Field(description="Reason provided by customer for the return")


class EscalateToHumanArgs(BaseModel):
    """Arguments when customer service must be handed off to a human agent."""

    reason: str = Field(description="Explicit reason why human intervention is required")
