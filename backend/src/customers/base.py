"""
TenantConfig — the data contract every client config module must provide.

Each customers/<slug>/config.py exports a CONFIG = TenantConfig(...) instance.
The loader discovers and caches these at startup.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine


@dataclass
class TenantConfig:
    """
    All per-tenant settings in one place.

    Required fields: slug, name
    Everything else has sensible defaults that inherit from domain/.

    When onboarding a new client, copy customers/acme/config.py and fill:
      - slug, name
      - enabled_channels
      - llm_provider / llm_model (if different from global settings)
      - system_prompt_override (the most impactful customisation)
      - flows (client-specific keyword → handler overrides)
      - extra (anything that doesn't fit above)
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    slug: str           # URL-safe, lowercase, e.g. "acme"
    name: str           # Human-readable, e.g. "ACME Corp"

    # ── Channels ──────────────────────────────────────────────────────────────
    # List the channel slugs this tenant uses. Others are ignored.
    enabled_channels: list[str] = field(default_factory=lambda: ["web_chat"])

    # ── LLM ───────────────────────────────────────────────────────────────────
    # Leave None to inherit from global settings (OPENAI_MODEL etc.)
    llm_provider: str | None = None   # "openai" | "azure_openai" | "ollama"
    llm_model: str | None = None      # "gpt-4o-mini" | "gpt-4o" | "llama3.2"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024

    # ── Prompts ───────────────────────────────────────────────────────────────
    # If set, REPLACES the domain base system prompt entirely.
    # If None, domain/prompts.py BASE_SYSTEM_PROMPT is used.
    system_prompt_override: str | None = None

    # ── Flows (routing overrides) ─────────────────────────────────────────────
    # Maps keyword (str) → async handler function.
    # Checked before domain/flows.py FLOWS — tenant wins.
    flows: dict[str, Callable[..., Coroutine[Any, Any, str]]] = field(default_factory=dict)

    # ── Feature flags ─────────────────────────────────────────────────────────
    rag_enabled: bool = False         # Enable RAG retrieval for this tenant
    history_window: int = 10          # How many turns to keep in context

    # ── Freeform extras ───────────────────────────────────────────────────────
    # Put anything client-specific here (webhook URLs, product IDs, tone flags…)
    extra: dict[str, Any] = field(default_factory=dict)

    def effective_system_prompt(self) -> str:
        """Return this tenant's system prompt (override or domain default)."""
        if self.system_prompt_override:
            return self.system_prompt_override
        from src.domain.prompts import BASE_SYSTEM_PROMPT
        return BASE_SYSTEM_PROMPT
