"""
Application settings — all configuration comes from environment variables.

Usage:
    from src.config.settings import settings
    print(settings.llm_provider)

For local dev copy .env.example to .env and fill in values.
In production, inject env vars via Docker/Kubernetes secrets.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    app_env: str = Field("development", description="development | staging | production")
    log_level: str = Field("INFO", description="DEBUG | INFO | WARNING | ERROR")
    secret_key: str = Field("change-me-in-production", description="Used for signing tokens")

    # ── LLM Provider ─────────────────────────────────────────────────────────
    # Which provider to use by default. Tenants can override in their config.
    llm_provider: str = Field("openai", description="openai | azure_openai | ollama")
    openai_api_key: str = Field("", description="OpenAI API key")
    openai_model: str = Field("gpt-4o-mini", description="Default model name")
    azure_openai_api_key: str = Field("", description="Azure OpenAI API key")
    azure_openai_endpoint: str = Field("", description="https://<resource>.openai.azure.com/")
    azure_openai_deployment: str = Field("", description="Azure deployment name")
    azure_openai_api_version: str = Field("2024-02-01")
    ollama_base_url: str = Field("http://localhost:11434", description="Ollama server URL")
    ollama_model: str = Field("llama3.2", description="Ollama model tag")

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = Field(
        "sqlite+aiosqlite:///./dev.db",
        description="SQLAlchemy async URL. Use postgresql+asyncpg://... for production.",
    )

    # ── Cache / Redis ─────────────────────────────────────────────────────────
    redis_url: str = Field("redis://localhost:6379/0", description="Optional, for session cache")

    # ── Channels ──────────────────────────────────────────────────────────────
    # Only fill in the channels you need. Others can be left empty.
    telegram_bot_token: str = Field("", description="Telegram BotFather token")
    slack_bot_token: str = Field("", description="xoxb-... Slack bot token")
    slack_signing_secret: str = Field("", description="Slack signing secret")
    twilio_account_sid: str = Field("", description="Twilio Account SID")
    twilio_auth_token: str = Field("", description="Twilio Auth Token")
    twilio_whatsapp_number: str = Field("", description="whatsapp:+14155238886")

    # ── RAG ───────────────────────────────────────────────────────────────────
    rag_enabled: bool = Field(False, description="Enable RAG retrieval globally")
    rag_vector_store: str = Field("chromadb", description="chromadb | pgvector | pinecone")
    rag_chroma_path: str = Field("./chroma_data", description="ChromaDB local storage path")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings singleton. Safe to call anywhere."""
    return Settings()


# Module-level alias for convenience: `from src.config.settings import settings`
settings = get_settings()
