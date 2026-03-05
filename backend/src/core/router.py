"""
Intent router — maps incoming message text to a handler function.

The router checks tenant-specific flows first, then falls back to domain defaults.
This allows per-client overrides without touching shared code.

Flow resolution order:
  1. customers/<slug>/flows.py  FLOWS dict  (tenant-specific)
  2. domain/flows.py            FLOWS dict  (shared default)
  3. domain/handlers.py         fallback()  (catch-all)
"""

from __future__ import annotations

from typing import Callable

from src.core.context import ConversationContext


# Handler type: async function that receives context and returns reply text
HandlerFn = Callable[[ConversationContext], "Coroutine[str]"]


def resolve_handler(ctx: ConversationContext) -> HandlerFn:
    """
    Return the appropriate handler function for the current message.

    Strategy: keyword matching (simple and fast for most chatbots).
    Replace or extend with an intent classifier / NLU model as needed.
    """
    text_lower = ctx.message.text.lower().strip()
    tenant_config = ctx.tenant_config

    # 1. Tenant-specific flows (imported lazily to avoid circular imports)
    if tenant_config is not None:
        tenant_flows: dict = getattr(tenant_config, "flows", {})
        for keyword, handler in tenant_flows.items():
            if keyword in text_lower:
                return handler

    # 2. Domain-level default flows
    from src.domain.flows import FLOWS as DOMAIN_FLOWS
    for keyword, handler in DOMAIN_FLOWS.items():
        if keyword in text_lower:
            return handler

    # 3. Catch-all fallback
    from src.domain.handlers import fallback
    return fallback
