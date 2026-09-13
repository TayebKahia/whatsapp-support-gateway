import time
from typing import Protocol

from gateway.models.domain import SessionRecord, SessionStatus


class SessionStore(Protocol):
    """Port for managing customer conversation state and transcripts."""

    def get_session(self, phone: str) -> SessionRecord:
        """Retrieve existing session or create a new active session."""
        ...

    def save_session(self, session: SessionRecord) -> None:
        """Persist updated session state."""
        ...

    def append_transcript(self, phone: str, role: str, message: str) -> None:
        """Append a message turn to the customer's session transcript."""
        ...

    def resolve_session(self, phone: str) -> None:
        """Mark an escalated or active session as resolved and reset to bot control."""
        ...


class InMemorySessionStore:
    """In-memory session store enforcing 24-hour customer service window timeout."""

    def __init__(self, window_seconds: float = 86400.0) -> None:
        self.window_seconds = window_seconds
        self._sessions: dict[str, SessionRecord] = {}

    def get_session(self, phone: str) -> SessionRecord:
        now = time.time()
        session = self._sessions.get(phone)

        # Check for 24-hour session window expiry
        if session is not None:
            if (now - session.last_interaction_ts) > self.window_seconds:
                # Expired: auto-reset to a fresh session
                session = SessionRecord(
                    phone_number=phone,
                    status=SessionStatus.ACTIVE_BOT,
                    transcript=[],
                    last_interaction_ts=now,
                )
                self._sessions[phone] = session
            return session

        # New customer session
        new_session = SessionRecord(
            phone_number=phone,
            status=SessionStatus.ACTIVE_BOT,
            transcript=[],
            last_interaction_ts=now,
        )
        self._sessions[phone] = new_session
        return new_session

    def save_session(self, session: SessionRecord) -> None:
        self._sessions[session.phone_number] = session

    def append_transcript(self, phone: str, role: str, message: str) -> None:
        session = self.get_session(phone)
        session.transcript.append({"role": role, "message": message})
        session.last_interaction_ts = time.time()
        self.save_session(session)

    def resolve_session(self, phone: str) -> None:
        session = self.get_session(phone)
        session.status = SessionStatus.ACTIVE_BOT
        session.escalation_reason = None
        self.save_session(session)
