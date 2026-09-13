from gateway.models.domain import SessionRecord, SessionStatus


class SessionStateMachine:
    """Manages conversational session states and prevents bot interference when escalated."""

    def can_auto_reply(self, session: SessionRecord) -> bool:
        """Returns True if the bot is allowed to automatically reply."""
        return session.status == SessionStatus.ACTIVE_BOT

    def transition_to_escalated(self, session: SessionRecord, reason: str) -> None:
        """Mute automated bot replies and flag session for human support."""
        session.status = SessionStatus.ESCALATED_HUMAN
        session.escalation_reason = reason

    def transition_to_active(self, session: SessionRecord) -> None:
        """Return session to automated bot control."""
        session.status = SessionStatus.ACTIVE_BOT
        session.escalation_reason = None

    def transition_to_closed(self, session: SessionRecord) -> None:
        """Close session upon completion or 24-hour timeout."""
        session.status = SessionStatus.CLOSED
