from fastapi.testclient import TestClient

from gateway.config import Settings
from gateway.main import create_app
from gateway.security.signature import calculate_meta_signature


def test_webhook_handshake_success() -> None:
    settings = Settings(
        webhook_verify_token="my_secure_verify_token",
        meta_app_secret="test_secret",
    )
    app = create_app(settings)
    client = TestClient(app)

    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "my_secure_verify_token",
            "hub.challenge": "115820124",
        },
    )

    assert response.status_code == 200
    assert response.text == "115820124"


def test_webhook_handshake_invalid_token() -> None:
    settings = Settings(
        webhook_verify_token="my_secure_verify_token",
        meta_app_secret="test_secret",
    )
    app = create_app(settings)
    client = TestClient(app)

    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "115820124",
        },
    )

    assert response.status_code == 403


def test_webhook_handshake_invalid_mode() -> None:
    settings = Settings(
        webhook_verify_token="my_secure_verify_token",
        meta_app_secret="test_secret",
    )
    app = create_app(settings)
    client = TestClient(app)

    response = client.get(
        "/webhook",
        params={
            "hub.mode": "publish",
            "hub.verify_token": "my_secure_verify_token",
            "hub.challenge": "115820124",
        },
    )

    assert response.status_code == 403


def test_webhook_post_unauthorized_signature() -> None:
    settings = Settings(
        meta_app_secret="test_secret",
        webhook_verify_token="verify_token",
    )
    app = create_app(settings)
    client = TestClient(app)

    response = client.post(
        "/webhook",
        content=b'{"some": "data"}',
        headers={"X-Hub-Signature-256": "sha256=invalidhexsignature"},
    )
    assert response.status_code == 401


def test_webhook_post_missing_signature_header() -> None:
    settings = Settings(
        meta_app_secret="test_secret",
        webhook_verify_token="verify_token",
    )
    app = create_app(settings)
    client = TestClient(app)

    response = client.post(
        "/webhook",
        content=b'{"some": "data"}',
    )
    assert response.status_code == 401


def test_webhook_post_valid_signature() -> None:
    secret = "test_secret"
    settings = Settings(
        meta_app_secret=secret,
        webhook_verify_token="verify_token",
    )
    app = create_app(settings)
    client = TestClient(app)

    payload = b'{"object": "whatsapp_business_account", "entry": []}'
    signature = calculate_meta_signature(payload, secret)

    response = client.post(
        "/webhook",
        content=payload,
        headers={"X-Hub-Signature-256": signature, "Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
