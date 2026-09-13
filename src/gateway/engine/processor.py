import logging
from collections.abc import Awaitable, Callable
from typing import Any

from gateway.channel.base import WhatsAppChannelPort
from gateway.engine.agent import BoundedToolAgent
from gateway.engine.router import Intent, IntentRouter
from gateway.engine.state_machine import SessionStateMachine
from gateway.models.domain import InboundMessageEvent, SessionRecord
from gateway.repository.order import OrderRepository
from gateway.repository.session import SessionStore

logger = logging.getLogger(__name__)

EscalationCallback = Callable[[SessionRecord, str], Awaitable[Any]]
OperatorMessageCallback = Callable[[str, dict[str, Any]], Awaitable[None]]


class MessageProcessor:
    """Core message processing pipeline connecting routing, state machine, and channel dispatch."""

    def __init__(
        self,
        channel: WhatsAppChannelPort,
        order_repo: OrderRepository,
        session_store: SessionStore,
        router: IntentRouter | None = None,
        agent: BoundedToolAgent | None = None,
        state_machine: SessionStateMachine | None = None,
        on_escalation: EscalationCallback | None = None,
        on_operator_broadcast: OperatorMessageCallback | None = None,
    ) -> None:
        self.channel = channel
        self.order_repo = order_repo
        self.session_store = session_store
        self.router = router or IntentRouter()
        self.agent = agent or BoundedToolAgent(order_repo)
        self.state_machine = state_machine or SessionStateMachine()
        self.on_escalation = on_escalation
        self.on_operator_broadcast = on_operator_broadcast

    async def process_event(self, event: InboundMessageEvent) -> None:
        phone = event.sender_phone
        session = self.session_store.get_session(phone)

        # 1. Immediately mark message as read (blue double ticks in WhatsApp)
        try:
            await self.channel.mark_read(event.wamid)
        except (RuntimeError, ConnectionResetError, OSError, ValueError, TimeoutError):
            logger.warning("Failed to mark message %s as read", event.wamid)

        # 2. Always append inbound message to customer transcript
        self.session_store.append_transcript(phone, role="user", message=event.body)

        # 3. Strict Muting Rule: If session is escalated to a human, suppress automated replies
        if not self.state_machine.can_auto_reply(session):
            logger.info("Session %s is ESCALATED_HUMAN. Automated bot reply suppressed.", phone)
            if self.on_operator_broadcast:
                try:
                    await self.on_operator_broadcast(
                        phone,
                        {"role": "customer", "text": event.body, "wamid": event.wamid},
                    )
                except Exception:
                    logger.exception("Failed to broadcast customer message to operator WebSockets")
            return

        # 3. Classify intent
        intent = self.router.route(event.body, interactive_id=event.interactive_id)
        logger.info("Routed event %s from %s as intent %s", event.wamid, phone, intent.value)

        # 4. Check for active security verification challenge
        if session.pending_verification_order_id and intent not in (
            Intent.HUMAN_ESCALATION,
            Intent.MENU,
        ):
            reply, buttons, _, document = await self.agent.verify_order_ownership(
                event.body, session
            )
            if buttons:
                await self.channel.send_interactive_buttons(phone, reply, buttons)
            else:
                await self.channel.send_text(phone, reply)

            if document:
                await self.channel.send_document(
                    phone,
                    document_url=document["document_url"],
                    filename=document["filename"],
                    caption=document.get("caption"),
                )

            self.session_store.append_transcript(phone, role="assistant", message=reply)
            self.session_store.save_session(session)
            return

        # 5. Execute workflow based on intent
        if intent == Intent.MENU:
            body = "Welcome to Customer Support! How can we help you today?"
            buttons = [
                {"id": "btn_track", "title": "Track Order"},
                {"id": "btn_return", "title": "Return / Refund"},
                {"id": "btn_human", "title": "Talk to Human"},
            ]
            await self.channel.send_interactive_buttons(phone, body, buttons)
            self.session_store.append_transcript(phone, role="assistant", message=body)
            self.session_store.save_session(session)

        elif intent == Intent.ORDER_QUERY:
            reply, buttons = await self.agent.handle_order_query(
                event.body, sender_phone=phone, session=session
            )
            if buttons:
                await self.channel.send_interactive_buttons(phone, reply, buttons)
            else:
                await self.channel.send_text(phone, reply)
            self.session_store.append_transcript(phone, role="assistant", message=reply)
            self.session_store.save_session(session)

        elif intent == Intent.RETURN_QUERY:
            reply, buttons, document = await self.agent.handle_return_query(
                event.body, sender_phone=phone, session=session
            )
            if buttons:
                await self.channel.send_interactive_buttons(phone, reply, buttons)
            else:
                await self.channel.send_text(phone, reply)

            if document:
                await self.channel.send_document(
                    phone,
                    document_url=document["document_url"],
                    filename=document["filename"],
                    caption=document.get("caption"),
                )

            self.session_store.append_transcript(phone, role="assistant", message=reply)
            self.session_store.save_session(session)

        elif intent == Intent.HUMAN_ESCALATION:
            self.state_machine.transition_to_escalated(session, reason=event.body)
            self.session_store.save_session(session)

            reply = (
                "You've been connected with our customer care team. "
                "A human agent will join shortly. Automated responses are now paused."
            )
            await self.channel.send_text(phone, reply)
            self.session_store.append_transcript(phone, role="assistant", message=reply)

            if self.on_escalation:
                try:
                    await self.on_escalation(session, event.body)
                except Exception:
                    logger.exception("Failed to dispatch external escalation event for %s", phone)

        else:
            # Fallback for unrecognized general queries
            reply = (
                "I'm not sure I understood that. You can track an order (e.g. *#ORD-1001*), "
                "inquire about a return, or type *human* to speak with our support team."
            )
            await self.channel.send_text(phone, reply)
            self.session_store.append_transcript(phone, role="assistant", message=reply)
