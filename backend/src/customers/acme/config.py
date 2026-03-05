"""
ACME Corp — tenant configuration.

═══════════════════════════════════════════════════════════════
CONSULTANT CHECKLIST — fill these in for each new client:
  [x] slug / name
  [ ] enabled_channels  — which channels the client uses
  [ ] llm_model         — gpt-4o-mini (cheap) vs gpt-4o (smarter)
  [ ] system_prompt_override in prompts.py
  [ ] flows             — any keyword shortcuts specific to this client
  [ ] extra             — client-specific data (product IDs, URLs, etc.)
═══════════════════════════════════════════════════════════════
"""

from src.customers.acme.flows import FLOWS as ACME_FLOWS
from src.customers.acme.prompts import SYSTEM_PROMPT
from src.customers.base import TenantConfig

CONFIG = TenantConfig(
    slug="acme",
    name="ACME Corp",

    # ── Channels ─────────────────────────────────────────────────────────────
    # Enable only channels the client has set up credentials for.
    enabled_channels=["web_chat", "telegram"],

    # ── LLM ──────────────────────────────────────────────────────────────────
    # None = inherit global settings.llm_provider / settings.openai_model
    llm_provider="openai",
    llm_model="gpt-4o-mini",       # upgrade to "gpt-4o" for more complex flows
    llm_temperature=0.6,           # lower = more predictable/less creative
    llm_max_tokens=512,

    # ── Prompts ───────────────────────────────────────────────────────────────
    system_prompt_override=SYSTEM_PROMPT,

    # ── Flows ─────────────────────────────────────────────────────────────────
    flows=ACME_FLOWS,

    # ── Feature flags ─────────────────────────────────────────────────────────
    rag_enabled=False,     # set True + configure rag/ if client has a knowledge base
    history_window=8,      # last N turns included in LLM context

    # ── Client-specific extras ─────────────────────────────────────────────
    extra={
        "support_email": "support@acme.example.com",
        "business_hours": "Mon-Fri 9h-18h BRT",
        "product_name": "ACME Platform",
    },
)
