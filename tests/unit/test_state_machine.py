from gateway.engine.state_machine import SessionStateMachine
from gateway.models.domain import SessionRecord, SessionStatus


def test_state_machine_initial_active() -> None:
    sm = SessionStateMachine()
    session = SessionRecord(phone_number="15551234567", last_interaction_ts=1000.0)

    assert sm.can_auto_reply(session) is True


def test_state_machine_escalate() -> None:
    sm = SessionStateMachine()
    session = SessionRecord(phone_number="15551234567", last_interaction_ts=1000.0)

    sm.transition_to_escalated(session, reason="User requested agent")
    assert session.status == SessionStatus.ESCALATED_HUMAN
    assert session.escalation_reason == "User requested agent"
    assert sm.can_auto_reply(session) is False


def test_state_machine_resolve() -> None:
    sm = SessionStateMachine()
    session = SessionRecord(
        phone_number="15551234567",
        status=SessionStatus.ESCALATED_HUMAN,
        last_interaction_ts=1000.0,
    )

    sm.transition_to_active(session)
    assert session.status == SessionStatus.ACTIVE_BOT
    assert session.escalation_reason is None
    assert sm.can_auto_reply(session) is True
