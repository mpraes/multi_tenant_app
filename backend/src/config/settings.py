"""
Configuração central do bot — edite este arquivo para personalizar sua instância.
Central bot configuration — edit this file to customize your chatbot instance.

Como usar / How to use:
  1. Preencha as variáveis de ambiente em backend/.env (ou exporte-as diretamente)
     Fill in environment variables in backend/.env (or export them directly)
  2. Edite CONFIG = BotConfig(...) abaixo para personalizar nome, prompt e fluxos
     Edit CONFIG = BotConfig(...) below to customize name, prompt, and flows
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Coroutine

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Campos do BotConfig que podem ser persistidos em config.json
# BotConfig fields that can be persisted in config.json
_PERSISTABLE = frozenset({
    "name", "system_prompt", "llm_provider", "llm_model",
    "llm_temperature", "llm_max_tokens", "rag_enabled", "history_window",
})

# Arquivo de overrides em tempo de execução / Runtime overrides file
# Localizado em backend/config.json, ao lado do .env
# Located at backend/config.json, next to .env
CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.json"


# ── Variáveis de ambiente / Environment variables ─────────────────────────────

class Settings(BaseSettings):
    """
    Todas as configurações vindas de variáveis de ambiente.
    All configuration read from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────────────
    app_env: str = Field("development", description="development | staging | production")
    log_level: str = Field("INFO", description="DEBUG | INFO | WARNING | ERROR")
    secret_key: str = Field("change-me-in-production", description="Used for signing tokens")

    # ── LLM Provider ──────────────────────────────────────────────────────────
    # Provedor padrão; pode ser sobrescrito em BotConfig abaixo
    # Default provider; can be overridden in BotConfig below
    llm_provider: str = Field(
        "openai",
        description="openai | azure_openai | ollama | groq | anthropic | bedrock",
    )

    # OpenAI
    openai_api_key: str = Field("", description="OpenAI API key")
    openai_model: str = Field("gpt-4o-mini", description="Default OpenAI model name")

    # Azure OpenAI
    azure_openai_api_key: str = Field("", description="Azure OpenAI API key")
    azure_openai_endpoint: str = Field("", description="https://<resource>.openai.azure.com/")
    azure_openai_deployment: str = Field("", description="Azure deployment name")
    azure_openai_api_version: str = Field("2024-02-01")

    # Ollama (local)
    ollama_base_url: str = Field("http://localhost:11434", description="Ollama server URL")
    ollama_model: str = Field("llama3.2", description="Ollama model tag")

    # Groq
    groq_api_key: str = Field("", description="Groq API key")
    groq_model: str = Field("llama-3.3-70b-versatile", description="Groq model name")

    # Anthropic (direct API)
    anthropic_api_key: str = Field("", description="Anthropic API key")
    anthropic_model: str = Field("claude-sonnet-4-6", description="Anthropic model ID")

    # AWS Bedrock
    aws_access_key_id: str = Field("", description="AWS access key ID")
    aws_secret_access_key: str = Field("", description="AWS secret access key")
    aws_region: str = Field("us-east-1", description="AWS region for Bedrock")
    bedrock_model_id: str = Field(
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="Bedrock model ARN or ID",
    )

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = Field(
        "sqlite+aiosqlite:///./dev.db",
        description="SQLAlchemy async URL. Use postgresql+asyncpg://... for production.",
    )

    # ── Cache / Redis ─────────────────────────────────────────────────────────
    redis_url: str = Field("redis://localhost:6379/0", description="Optional, for session cache")

    # ── Channels ──────────────────────────────────────────────────────────────
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
    """Retorna o singleton de Settings (cacheado). / Returns a cached Settings singleton."""
    return Settings()


# Alias de módulo / Module-level alias: `from src.config.settings import settings`
settings = get_settings()


# ── Personalização do bot / Bot customization ─────────────────────────────────

@dataclass
class BotConfig:
    """
    Toda personalização do bot em um único lugar.
    All bot customization in one place.
    """

    # Nome exibido nas respostas de saudação / Display name used in greeting responses
    name: str = "My Chatbot"

    # Substitui o prompt padrão em domain/prompts.py / Overrides default prompt in domain/prompts.py
    system_prompt: str | None = None

    # Fluxos: palavra-chave → handler assíncrono / Flows: keyword → async handler
    flows: dict[str, Callable[..., Coroutine[Any, Any, str]]] = field(default_factory=dict)

    # Sobrescritas de LLM (None = herda de settings) / LLM overrides (None = inherits from settings)
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024

    # Ativa recuperação RAG / Enable RAG retrieval
    rag_enabled: bool = False

    # Quantidade de turnos mantidos no contexto / Number of turns kept in context
    history_window: int = 10

    # Campos livres para dados extras / Free-form extras
    extra: dict[str, Any] = field(default_factory=dict)

    def effective_system_prompt(self) -> str:
        """
        Retorna o system prompt ativo (override ou padrão do domínio).
        Returns the active system prompt (override or domain default).
        """
        if self.system_prompt:
            return self.system_prompt
        from src.domain.prompts import BASE_SYSTEM_PROMPT
        return BASE_SYSTEM_PROMPT


# ── Personalize seu bot aqui / Customize your bot here ───────────────────────

CONFIG = BotConfig(
    name="My Chatbot",
    # system_prompt="Você é um assistente de suporte da Acme Corp...",
    # flows={"keyword": my_async_handler},
    # llm_provider="openai",
    # llm_model="gpt-4o-mini",
)

# Aplica overrides de config.json sobre os defaults acima
# Applies config.json overrides on top of the defaults above
if CONFIG_PATH.exists():
    try:
        _overrides: dict = json.loads(CONFIG_PATH.read_text())
        for _k, _v in _overrides.items():
            if _k in _PERSISTABLE:
                setattr(CONFIG, _k, _v)
    except Exception:
        pass  # arquivo inválido é ignorado silenciosamente / invalid file silently ignored
