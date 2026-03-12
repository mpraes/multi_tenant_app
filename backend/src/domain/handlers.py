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
    config = ctx.config

    # Provedor: override em bot_config.py → global settings.py
    # Provider: bot_config.py override → global settings.py
    provider = get_llm_provider(config.llm_provider)

    system_prompt = config.effective_system_prompt()
    messages = ctx.history_as_openai_messages()

    # Se houver contexto RAG, prepend ao system prompt / Prepend RAG context if available
    if ctx.retrieved_context:
        system_prompt = (
            f"{system_prompt}\n\n"
            f"Contexto relevante recuperado da base de conhecimento:\n{ctx.retrieved_context}"
        )

    response = await provider.chat(
        system_prompt=system_prompt,
        messages=messages,
        temperature=config.llm_temperature,
        max_tokens=config.llm_max_tokens,
    )

    logger.debug(
        "LLM %s | in=%d out=%d tokens",
        provider.model_name(),
        response.input_tokens,
        response.output_tokens,
    )

    return response.text


async def greeting(ctx: ConversationContext) -> str:
    """
    Acionado em palavras-chave de saudação.
    Triggered on explicit greeting keywords.
    """
    from src.utils.time import greeting_for_hour
    time_greeting = greeting_for_hour()
    name = ctx.config.name
    return f"{time_greeting}! Welcome to {name}. How can I help you today?"


async def fallback(ctx: ConversationContext) -> str:
    """
    Catch-all handler — called when no flow keyword matches.
    Default behaviour: pass to the LLM for a free-form response.
    """
    return await llm_reply(ctx)
