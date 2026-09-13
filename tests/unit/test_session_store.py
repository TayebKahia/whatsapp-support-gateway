import time

from gateway.models.domain import SessionStatus
from gateway.repository.session import InMemorySessionStore


def test_get_session_new_user() -> None:
    store = InMemorySessionStore()
    session = store.get_session("15551234567")

    assert session.phone_number == "15551234567"
    assert session.status == SessionStatus.ACTIVE_BOT
    assert session.transcript == []


def test_append_transcript() -> None:
    store = InMemorySessionStore()
    phone = "15551234567"

    store.append_transcript(phone, role="user", message="Hello support")
    store.append_transcript(phone, role="assistant", message="Hi! How can I help?")

    session = store.get_session(phone)
    assert len(session.transcript) == 2
    assert session.transcript[0]["role"] == "user"
    assert session.transcript[0]["message"] == "Hello support"
    assert session.transcript[1]["role"] == "assistant"


def test_session_status_update_and_resolve() -> None:
    store = InMemorySessionStore()
    phone = "15551234567"

    session = store.get_session(phone)
    session.status = SessionStatus.ESCALATED_HUMAN
    session.escalation_reason = "Customer asked for human agent"
    store.save_session(session)

    reloaded = store.get_session(phone)
    assert reloaded.status == SessionStatus.ESCALATED_HUMAN
    assert reloaded.escalation_reason == "Customer asked for human agent"

    store.resolve_session(phone)
    resolved = store.get_session(phone)
    assert resolved.status == SessionStatus.ACTIVE_BOT
    assert resolved.escalation_reason is None


def test_session_24h_window_reset() -> None:
    store = InMemorySessionStore()
    phone = "15551234567"

    store.append_transcript(phone, role="user", message="Old message from 2 days ago")
    session = store.get_session(phone)
    # Simulate last interaction 25 hours ago
    session.last_interaction_ts = time.time() - (25 * 3600)
    session.status = SessionStatus.ESCALATED_HUMAN
    store.save_session(session)

    # Next lookup should auto-reset to a clean 24h session
    fresh_session = store.get_session(phone)
    assert fresh_session.status == SessionStatus.ACTIVE_BOT
    assert fresh_session.transcript == []
