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

        clean = text.strip().lower()

        # General top-level actions should NOT be treated as pronoun referents
        general_intents = {
            "track",
            "track order",
            "track my order",
            "where is my package",
            "where is my order",
            "return",
            "refund",
            "return / refund",
            "return item",
        }
        if clean in general_intents:
            return None

        # Contextual resolution: If pronoun/referent is used and session has an active order
        if session and session.last_referenced_order_id:
            context_keywords = [
                "it",
                "this",
                "status",
                "arrive",
                "when",
                "package",
            ]
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

        # Smart Phone Lookup: If no order ID was specified, check customer phone number
        if not order_id and sender_phone:
            customer_orders = self.order_repo.get_orders_by_customer_phone(sender_phone)
            if len(customer_orders) == 1:
                # Scenario A: Exactly 1 order linked to phone -> Instant zero-friction resolution!
                matched_order = customer_orders[0]
                if session:
                    session.last_referenced_order_id = matched_order.order_id
                    if matched_order.order_id not in session.verified_order_ids:
                        session.verified_order_ids.append(matched_order.order_id)
                reply, buttons = self._build_order_status_reply(matched_order)
                return (
                    f"📦 We found 1 active order for your phone number:\n\n{reply}",
                    buttons,
                )
            elif len(customer_orders) > 1:
                # Scenario B: Multiple packages linked to phone -> Interactive disambiguation!
                buttons = [
                    {"id": f"track_{o.order_id}", "title": f"📦 #{o.order_id}"}
                    for o in customer_orders[:3]
                ]
                order_list_str = "\n".join(
                    f"• *#{o.order_id}* ({', '.join(o.items) if o.items else 'Items'}) — {o.status.value}"
                    for o in customer_orders
                )
                return (
                    (
                        f"📦 We found *{len(customer_orders)} packages* associated with your phone number:\n\n"
                        f"{order_list_str}\n\n"
                        "Which order would you like to track? Tap a button below or reply with the order number:"
                    ),
                    buttons,
                )
            else:
                # Scenario C: 0 orders linked to phone -> Prompt for order number
                return (
                    (
                        "We could not find any active orders associated with your WhatsApp number. "
                        "If you placed your order under a different number or email, please reply with your order number "
                        "(for example: *#ORD-1001*)."
                    ),
                    None,
                )

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
    ) -> tuple[str, list[dict[str, str]] | None, bool, dict[str, str] | None]:
        order_id = session.pending_verification_order_id
        if not order_id:
            return ("No pending verification found. How can I help you?", None, False, None)

        order = self.order_repo.get_order(order_id)
        if not order:
            session.pending_verification_order_id = None
            return (f"Order *{order_id}* was not found in our records.", None, False, None)

        clean_digits = re.sub(r"\D", "", verification_input)
        customer_digits = _normalize_phone(order.customer_phone)

        if len(clean_digits) >= 4 and customer_digits.endswith(clean_digits[-4:]):
            session.pending_verification_order_id = None
            if order.order_id not in session.verified_order_ids:
                session.verified_order_ids.append(order.order_id)
            session.last_referenced_order_id = order.order_id

            # If this is a delivered order, approve return and provide PDF label
            if order.status.value == "DELIVERED":
                result = self.order_repo.evaluate_return(
                    order.order_id, reason="Customer return request"
                )
                if result.get("eligible"):
                    buttons = [
                        {"id": "btn_track", "title": "Track Order"},
                        {"id": "btn_human", "title": "Talk to Human"},
                        {"id": "btn_menu", "title": "Main Menu"},
                    ]
                    doc_payload = {
                        "document_url": f"/media/return-labels/{order.order_id}.pdf",
                        "filename": f"return_label_{order.order_id}.pdf",
                        "caption": f"📄 Prepaid Return Label for #{order.order_id}",
                    }
                    full_reply = (
                        f"✅ *Security Verification Successful!*\n\n"
                        f"✅ *Return Approved for #{order.order_id}*\n\n"
                        f"{result['instructions']}"
                    )
                    return full_reply, buttons, True, doc_payload

            reply, buttons = self._build_order_status_reply(order)
            full_reply = f"✅ *Security Verification Successful!*\n\n{reply}"
            return full_reply, buttons, True, None

        if len(clean_digits) < 4:
            return (
                (
                    f"🔒 *Verification is pending for order #{order.order_id}*.\n"
                    "Please reply with the *last 4 digits* of the phone number on file to proceed, "
                    "or type *cancel* to return to the main menu."
                ),
                [
                    {"id": "btn_menu", "title": "Main Menu"},
                    {"id": "btn_human", "title": "Talk to Human"},
                ],
                False,
                None,
            )

        fail_msg = (
            f"❌ Verification failed. The digits provided did not match our records for order *#{order.order_id}*. "
            "Please verify the last 4 digits and try again, or type *human* to speak with our support team."
        )
        return fail_msg, None, False, None

    async def handle_return_query(
        self,
        query: str,
        sender_phone: str | None = None,
        session: SessionRecord | None = None,
    ) -> tuple[str, list[dict[str, str]] | None, dict[str, str] | None]:
        order_id = self.extract_order_id(query, session=session)

        # Smart Phone Lookup: If no order ID was specified, check customer phone number
        if not order_id and sender_phone:
            customer_orders = self.order_repo.get_orders_by_customer_phone(sender_phone)
            if len(customer_orders) == 1:
                order_id = customer_orders[0].order_id
            elif len(customer_orders) > 1:
                # Multiple packages: interactive disambiguation
                buttons = [
                    {"id": f"return_{o.order_id}", "title": f"↩️ #{o.order_id}"}
                    for o in customer_orders[:3]
                ]
                order_list_str = "\n".join(
                    f"• *#{o.order_id}* ({', '.join(o.items) if o.items else 'Items'}) — {o.status.value}"
                    for o in customer_orders
                )
                return (
                    (
                        f"↩️ We found *{len(customer_orders)} orders* associated with your phone number:\n\n"
                        f"{order_list_str}\n\n"
                        "Which order would you like to return or exchange? Tap a button below:"
                    ),
                    buttons,
                    None,
                )
            else:
                return (
                    (
                        "We could not find any active orders associated with your WhatsApp number. "
                        "To assist with returns or refunds, please reply with your order number "
                        "(for example: *#ORD-1003*)."
                    ),
                    None,
                    None,
                )

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
