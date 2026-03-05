"""
Globex Corp — tenant configuration.

Globex example intentionally uses different settings than ACME to
demonstrate the range of per-tenant customisation available.
"""

from src.customers.base import TenantConfig
from src.customers.globex.flows import FLOWS as GLOBEX_FLOWS
from src.customers.globex.prompts import SYSTEM_PROMPT

CONFIG = TenantConfig(
    slug="globex",
    name="Globex Corp",

    enabled_channels=["web_chat", "whatsapp", "slack"],

    # Globex has more complex queries — use a more capable model
    llm_provider="openai",
    llm_model="gpt-4o",
    llm_temperature=0.4,     # low temperature = more precise, less creative
    llm_max_tokens=1024,

    system_prompt_override=SYSTEM_PROMPT,

    flows=GLOBEX_FLOWS,

    rag_enabled=True,        # Globex has a product knowledge base
    history_window=12,

    extra={
        "support_url": "https://help.globex.example.com",
        "crm_webhook": "https://crm.globex.example.com/webhooks/chat",
        "language": "en",
        "tier": "enterprise",
    },
)
