"""
Domain-level handlers — generic actions shared across all tenants.

These handlers call the LLM using the tenant's configured provider and
system prompt. Tenants can override any of these in their flows.py.

Handler signature: async (ctx: ConversationContext) -> str
"""

from __future__ import annotations

from src.core.context import ConversationContext
from src.llm import get_llm_provider
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def llm_reply(ctx: ConversationContext) -> str:
    """
    Main LLM handler — send conversation history to the model and return its reply.

    This is the default handler for any message that doesn't match a flow keyword.
    """
    tenant = ctx.tenant_config

    # Pick the right provider: tenant override → global settings
    provider_slug = tenant.llm_provider if tenant else None
    provider = get_llm_provider(provider_slug)

    system_prompt = tenant.effective_system_prompt() if tenant else ""
    messages = ctx.history_as_openai_messages()

    # If there's RAG context, prepend it to the system prompt
    if ctx.retrieved_context:
        system_prompt = (
            f"{system_prompt}\n\n"
            f"Relevant context retrieved from the knowledge base:\n{ctx.retrieved_context}"
        )

    temperature = tenant.llm_temperature if tenant else 0.7
    max_tokens = tenant.llm_max_tokens if tenant else 1024

    response = await provider.chat(
        system_prompt=system_prompt,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    logger.debug(
        "[%s] LLM %s | in=%d out=%d tokens",
        ctx.tenant_slug, provider.model_name(),
        response.input_tokens, response.output_tokens,
    )

    return response.text


async def greeting(ctx: ConversationContext) -> str:
    """Triggered on explicit greeting keywords. Can be overridden per tenant."""
    from src.utils.time import greeting_for_hour
    time_greeting = greeting_for_hour()
    name = ctx.tenant_config.name if ctx.tenant_config else "there"
    return f"{time_greeting}! Welcome to {name}. How can I help you today?"


async def fallback(ctx: ConversationContext) -> str:
    """
    Catch-all handler — called when no flow keyword matches.
    Default behaviour: pass to the LLM for a free-form response.
    """
    return await llm_reply(ctx)
