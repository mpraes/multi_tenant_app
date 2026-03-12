"""
Middleware protocol — before/after hooks for the message lifecycle.

Middleware runs in declared order on every message, regardless of tenant.
Use it for cross-cutting concerns: logging, auth, rate limiting, metrics.

To add a middleware:
  1. Create a class implementing MessageMiddleware
  2. Register it in src/core/engine.py  Engine.middleware_stack
"""

from __future__ import annotations

from typing import Protocol

from src.core.context import ConversationContext


class MessageMiddleware(Protocol):
    """
    Duck-typed middleware protocol.
    Implementing this Protocol is optional — any object with before/after works.
    """

    async def before(self, ctx: ConversationContext) -> None:
        """Called before the engine processes the message. Mutate ctx.state freely."""
        ...

    async def after(self, ctx: ConversationContext, reply_text: str) -> None:
        """Called after the LLM reply is generated. Use for logging/metrics."""
        ...


class LoggingMiddleware:
    """
    Registra cada mensagem recebida e resposta enviada.
    Logs every incoming message and outgoing reply.
    """

    async def before(self, ctx: ConversationContext) -> None:
        from src.utils.logging import get_logger
        logger = get_logger("middleware.logging")
        logger.info(
            "session=%s user=%s | IN: %s",
            ctx.message.session_id,
            ctx.message.user_id,
            ctx.message.text[:120],
        )

    async def after(self, ctx: ConversationContext, reply_text: str) -> None:
        from src.utils.logging import get_logger
        logger = get_logger("middleware.logging")
        logger.info(
            "session=%s | OUT: %s",
            ctx.message.session_id,
            reply_text[:120],
        )
