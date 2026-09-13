import re

from gateway.models.domain import OrderRecord, SessionRecord
from gateway.models.tools import CheckReturnEligibilityArgs, LookupOrderArgs
from gateway.repository.order import OrderRepository


def _normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone)


class BoundedToolAgent:
    """Bounded AI tool-calling agent enforcing typed schemas on all backend operations."""

    def __init__(self, order_repo: OrderRepository) -> None:
        self.order_repo = order_repo
        # Flexible pattern matching: ORD-1001, ord 1001, order 1001, order #1001, #1001
        self._order_pattern = re.compile(
            r"(?:#?\s*(?:ORD|ORDER)[\s-]*#?(\d+))|(?:#?(\d{4,}))",
            re.IGNORECASE,
        )

    def extract_order_id(self, text: str, session: SessionRecord | None = None) -> str | None:
        match = self._order_pattern.search(text)
        if match:
            digits = match.group(1) or match.group(2)
            return f"ORD-{digits}"

        # Contextual resolution: If pronoun/referent is used and session has an active order
        if session and session.last_referenced_order_id:
            context_keywords = [
                "it",
                "this",
                "status",
                "track",
                "arrive",
                "when",
                "return",
                "refund",
                "package",
                "order",
            ]
            clean = text.lower()
            if any(k in clean for k in context_keywords):
                return session.last_referenced_order_id

        return None

    def _build_order_status_reply(self, order: OrderRecord) -> tuple[str, list[dict[str, str]]]:
        carrier_str = order.carrier if order.carrier else "Preparing for dispatch"
        tracking_str = (
            order.tracking_number if order.tracking_number else "Will be assigned upon pickup"
        )
        eta_str = order.estimated_delivery if order.estimated_delivery else "To be determined"
        items_str = ", ".join(order.items) if order.items else "N/A"

        reply = (
            f"📦 *Order Status: #{order.order_id}*\n"
            f"• Status: *{order.status.value}*\n"
            f"• Carrier: {carrier_str}\n"
            f"• Tracking #: {tracking_str}\n"
            f"• Est. Delivery: {eta_str}\n"
            f"• Items: {items_str}"
        )
        buttons = [
            {"id": "btn_return", "title": "Return / Refund"},
            {"id": "btn_human", "title": "Talk to Human"},
            {"id": "btn_menu", "title": "Main Menu"},
        ]
        return reply, buttons

    async def handle_order_query(
        self,
        query: str,
        sender_phone: str | None = None,
        session: SessionRecord | None = None,
    ) -> tuple[str, list[dict[str, str]] | None]:
        order_id = self.extract_order_id(query, session=session)
        if not order_id:
            return (
                (
                    "To check your shipment status, please reply with your order number "
                    "(for example: *#ORD-1001*)."
                ),
                None,
            )

        args = LookupOrderArgs(order_id=order_id)
        order = self.order_repo.get_order(args.order_id)

        if not order:
            return (
                (
                    f"We could not find order *{args.order_id}* in our records. "
                    "Please double-check the order number and try again."
                ),
                None,
            )

        # Security check: verify phone ownership if sender_phone and session are provided
        if sender_phone and session:
            sender_clean = _normalize_phone(sender_phone)
            order_customer_clean = _normalize_phone(order.customer_phone)

            is_owner = sender_clean == order_customer_clean
            is_already_verified = order.order_id in session.verified_order_ids

            if not (is_owner or is_already_verified):
                session.pending_verification_order_id = order.order_id
                challenge = (
                    f"🔒 *Security Verification Required*\n"
                    f"For your privacy, order *#{order.order_id}* is associated with a different phone number. "
                    f"Please reply with the *last 4 digits* of the phone number on file to verify ownership."
                )
                return challenge, None

            # User is authorized
            if order.order_id not in session.verified_order_ids:
                session.verified_order_ids.append(order.order_id)
            session.last_referenced_order_id = order.order_id
            session.pending_verification_order_id = None

        return self._build_order_status_reply(order)

    async def verify_order_ownership(
        self, verification_input: str, session: SessionRecord
    ) -> tuple[str, list[dict[str, str]] | None, bool]:
        order_id = session.pending_verification_order_id
        if not order_id:
            return ("No pending verification found. How can I help you?", None, False)

        order = self.order_repo.get_order(order_id)
        if not order:
            session.pending_verification_order_id = None
            return (f"Order *{order_id}* was not found in our records.", None, False)

        clean_digits = re.sub(r"\D", "", verification_input)
        customer_digits = _normalize_phone(order.customer_phone)

        if len(clean_digits) >= 4 and customer_digits.endswith(clean_digits[-4:]):
            session.pending_verification_order_id = None
            if order.order_id not in session.verified_order_ids:
                session.verified_order_ids.append(order.order_id)
            session.last_referenced_order_id = order.order_id

            reply, buttons = self._build_order_status_reply(order)
            full_reply = f"✅ *Security Verification Successful!*\n\n{reply}"
            return full_reply, buttons, True

        fail_msg = (
            f"❌ Verification failed. The digits provided did not match our records for order *#{order.order_id}*. "
            "Please verify the last 4 digits and try again, or type *human* to speak with our support team."
        )
        return fail_msg, None, False

    async def handle_return_query(
        self,
        query: str,
        sender_phone: str | None = None,
        session: SessionRecord | None = None,
    ) -> tuple[str, list[dict[str, str]] | None, dict[str, str] | None]:
        order_id = self.extract_order_id(query, session=session)
        if not order_id:
            return (
                (
                    "To assist with returns or refunds, please provide your order number "
                    "(for example: *#ORD-1003*)."
                ),
                None,
                None,
            )

        args = CheckReturnEligibilityArgs(order_id=order_id, reason=query)
        order = self.order_repo.get_order(args.order_id)
        if not order:
            return (
                f"We could not find order *{args.order_id}* in our records.",
                None,
                None,
            )

        # Security check: verify phone ownership if sender_phone and session provided
        if sender_phone and session:
            sender_clean = _normalize_phone(sender_phone)
            order_customer_clean = _normalize_phone(order.customer_phone)

            is_owner = sender_clean == order_customer_clean
            is_already_verified = order.order_id in session.verified_order_ids

            if not (is_owner or is_already_verified):
                session.pending_verification_order_id = order.order_id
                challenge = (
                    f"🔒 *Security Verification Required*\n"
                    f"For your privacy, order *#{order.order_id}* is associated with a different phone number. "
                    f"Please reply with the *last 4 digits* of the phone number on file to verify return eligibility."
                )
                return challenge, None, None

            if order.order_id not in session.verified_order_ids:
                session.verified_order_ids.append(order.order_id)
            session.last_referenced_order_id = order.order_id
            session.pending_verification_order_id = None

        result = self.order_repo.evaluate_return(args.order_id, reason=args.reason)
        buttons = [
            {"id": "btn_track", "title": "Track Order"},
            {"id": "btn_human", "title": "Talk to Human"},
            {"id": "btn_menu", "title": "Main Menu"},
        ]

        if result["eligible"]:
            doc_payload = {
                "document_url": f"/media/return-labels/{order.order_id}.pdf",
                "filename": f"return_label_{order.order_id}.pdf",
                "caption": f"📄 Prepaid Return Label for #{order.order_id}",
            }
            return (
                f"✅ *Return Approved for #{args.order_id}*\n\n{result['instructions']}",
                buttons,
                doc_payload,
            )

        return (
            f"ℹ️ *Return Ineligible for #{args.order_id}*\n\n{result['reason']}",
            buttons,
            None,
        )
