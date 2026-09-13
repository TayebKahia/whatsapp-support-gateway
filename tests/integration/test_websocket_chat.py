from fastapi.testclient import TestClient

from gateway.channel.mock import MockWhatsAppAdapter
from gateway.main import create_app
from gateway.models.domain import SessionStatus
from gateway.repository.session import InMemorySessionStore


def test_operator_websocket_two_way_chat() -> None:
    channel = MockWhatsAppAdapter()
    store = InMemorySessionStore()
    phone = "+15551234567"

    app = create_app(channel=channel, session_store=store)
    client = TestClient(app)

    with client.websocket_connect(f"/ws/operator/{phone}") as websocket:
        # 1. Verify connection established handshake
        init_data = websocket.receive_json()
        assert init_data["type"] == "connection_established"
        assert init_data["phone"] == phone

        # 2. Operator sends message to customer
        websocket.send_json({"text": "Hello, I am Sarah from customer support. How can I help?"})

        # Receive broadcast/echo on the websocket
        echo_data = websocket.receive_json()
        assert echo_data["type"] == "operator_message"
        assert echo_data["role"] == "agent"
        assert "Sarah" in echo_data["text"]

        # Verify mock channel dispatched message to customer
        assert len(channel.sent_messages) == 1
        assert channel.sent_messages[0]["to"] == phone
        assert "Sarah" in channel.sent_messages[0]["body"]

        # Verify transcript recorded agent message
        session = store.get_session(phone)
        assert any(t["role"] == "agent" and "Sarah" in t["message"] for t in session.transcript)


def test_customer_message_broadcasts_to_operator_websocket() -> None:
    channel = MockWhatsAppAdapter()
    store = InMemorySessionStore()
    phone = "+15559876543"

    # Pre-escalate session
    session = store.get_session(phone)
    session.status = SessionStatus.ESCALATED_HUMAN
    store.save_session(session)

    app = create_app(channel=channel, session_store=store)
    client = TestClient(app)

    with client.websocket_connect(f"/ws/operator/{phone}") as websocket:
        init_data = websocket.receive_json()
        assert init_data["type"] == "connection_established"

        # Customer sends message via demo send endpoint
        resp = client.post(
            "/demo/send",
            json={"phone_number": phone, "message": "Where is my refund?"},
        )
        assert resp.status_code == 200
        assert resp.json()["bot_muted"] is True

        # Operator socket should receive the customer message broadcast
        broadcast = websocket.receive_json()
        assert broadcast["role"] == "customer"
        assert broadcast["text"] == "Where is my refund?"
