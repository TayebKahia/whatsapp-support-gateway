from typing import Literal

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime configuration loaded from environment variables."""

    # Server Settings
    port: int = 8000
    environment: Literal["development", "staging", "production", "test"] = "development"

    # WhatsApp Channel Settings
    whatsapp_provider: Literal["mock", "meta"] = "mock"
    meta_app_secret: str = "dev_app_secret"
    meta_access_token: str = "dev_access_token"
    phone_number_id: str = "1000123456789"
    webhook_verify_token: str = "dev_verify_token"

    # AI / LLM Settings
    llm_provider: Literal["mock", "ollama", "groq", "openai"] = "mock"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "qwen2.5:7b"

    # External Webhook Integration (e.g. n8n / Zapier)
    integration_webhook_url: HttpUrl | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
