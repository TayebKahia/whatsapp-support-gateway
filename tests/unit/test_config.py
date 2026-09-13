import pytest

from gateway.config import Settings


def test_default_settings() -> None:
    settings = Settings(
        meta_app_secret="test_secret",
        meta_access_token="test_token",
        phone_number_id="123456789",
    )
    assert settings.port == 8000
    assert settings.environment == "development"
    assert settings.whatsapp_provider == "mock"
    assert settings.llm_provider == "mock"
    assert settings.webhook_verify_token == "dev_verify_token"
    assert settings.integration_webhook_url is None


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("WHATSAPP_PROVIDER", "meta")
    monkeypatch.setenv("META_APP_SECRET", "custom_secret_123")
    monkeypatch.setenv("META_ACCESS_TOKEN", "token_abc")
    monkeypatch.setenv("PHONE_NUMBER_ID", "987654321")
    monkeypatch.setenv("INTEGRATION_WEBHOOK_URL", "https://n8n.example.com/webhook")

    settings = Settings()
    assert settings.port == 9000
    assert settings.whatsapp_provider == "meta"
    assert settings.meta_app_secret == "custom_secret_123"
    assert settings.meta_access_token == "token_abc"
    assert settings.phone_number_id == "987654321"
    assert str(settings.integration_webhook_url) == "https://n8n.example.com/webhook"
