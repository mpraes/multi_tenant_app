"""
Message processing pipeline.

The Engine is the heart of the framework. Given a ConversationContext it:
  1. Runs all before-middleware
  2. Builds the conversation history
  3. Resolves and calls the handler (which calls the LLM)
  4. Runs all after-middleware
  5. Returns the reply text

The Engine is stateless — all state lives in ConversationContext.
"""

from __future__ import annotations

from src.core.context import ConversationContext
from src.core.message import MessageRole
from src.core.middleware import LoggingMiddleware, MessageMiddleware
from src.core.router import resolve_handler
from src.core.tenant_middleware import TenantMiddleware


class Engine:
    """
    Wires middleware, routing, and LLM calls into a single pipeline.

    The middleware_stack is executed in order. TenantMiddleware MUST be first.
    Add new middleware here (e.g. RateLimitMiddleware, AuthMiddleware).
    """

    middleware_stack: list[MessageMiddleware] = [
        TenantMiddleware(),
        LoggingMiddleware(),
        # Add more middleware here:
        # RateLimitMiddleware(),
        # MetricsMiddleware(),
    ]

    async def process(self, ctx: ConversationContext) -> str:
        """
        Run the full pipeline and return the assistant's reply text.

        Args:
            ctx: ConversationContext pre-populated with the incoming Message.
        """
        # 1. Before-middleware (tenant resolution, logging, auth, etc.)
        for mw in self.middleware_stack:
            await mw.before(ctx)

        # 2. Record the user turn in context history
        ctx.add_turn(MessageRole.USER, ctx.message.text)

        # 3. Route to the right handler and get the reply
        handler = resolve_handler(ctx)
        reply_text: str = await handler(ctx)

        # 4. Record the assistant turn
        ctx.add_turn(MessageRole.ASSISTANT, reply_text)

        # 5. After-middleware (logging, metrics, persistence, etc.)
        for mw in reversed(self.middleware_stack):
            await mw.after(ctx, reply_text)

        return reply_text
