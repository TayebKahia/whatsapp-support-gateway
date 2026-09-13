import pytest
from httpx import ASGITransport, AsyncClient

from gateway.main import create_app


@pytest.mark.asyncio
async def test_demo_page_serves_html() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/demo")
        assert response.status_code == 200
        assert "text/html" in response.headers["Content-Type"]
        assert "WhatsApp Support Gateway" in response.text
        assert "Simulator" in response.text


@pytest.mark.asyncio
async def test_demo_send_and_telemetry() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "phone_number": "15551234567",
            "message": "Where is my order #ORD-1001?",
        }
        response = await client.post("/demo/send", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["wamid"].startswith("wamid.")
        assert data["signature_valid"] is True
        assert data["intent"] == "ORDER_QUERY"
        assert "ORD-1001" in data["bot_reply"]
        assert "buttons" in data
        assert data["buttons"] is not None
        assert any(b["id"] == "btn_return" for b in data["buttons"])
        assert data["latency_ms"] > 0
        assert data["session_status"] == "ACTIVE_BOT"


@pytest.mark.asyncio
async def test_demo_escalation_and_operator_resolve() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    phone = "15550007777"
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Send escalation message
        resp1 = await client.post(
            "/demo/send",
            json={"phone_number": phone, "message": "I want to talk to a human"},
        )
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["session_status"] == "ESCALATED_HUMAN"

        # Subsequent message should show bot is muted
        resp2 = await client.post(
            "/demo/send",
            json={"phone_number": phone, "message": "Anyone there?"},
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["bot_muted"] is True
        assert data2["bot_reply"] is None

        # Operator resolves the session
        resolve_resp = await client.post(f"/demo/resolve/{phone}")
        assert resolve_resp.status_code == 200
        assert resolve_resp.json()["status"] == "resolved"

        # Next message is answered by bot again
        resp3 = await client.post(
            "/demo/send",
            json={"phone_number": phone, "message": "menu"},
        )
        assert resp3.status_code == 200
        data3 = resp3.json()
        assert data3["session_status"] == "ACTIVE_BOT"
        assert data3["bot_muted"] is False


@pytest.mark.asyncio
async def test_demo_return_delivers_document_and_media_route() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    # ORD-1003 belongs to 15551112233
    phone = "15551112233"
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/demo/send",
            json={"phone_number": phone, "message": "Return ORD-1003"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "RETURN_QUERY"
        assert "Approved" in data["bot_reply"]
        assert data["document"] is not None
        assert "ORD-1003.pdf" in data["document"]["document_url"]

        # Fetch the actual media PDF route
        pdf_resp = await client.get(data["document"]["document_url"])
        assert pdf_resp.status_code == 200
        assert "application/pdf" in pdf_resp.headers["Content-Type"]
        assert pdf_resp.content.startswith(b"%PDF-")
