"""
Tenant resolution middleware — loads TenantConfig into context before the engine runs.

This middleware must be FIRST in the stack so all subsequent middleware
and the engine itself can access ctx.tenant_config.
"""

from __future__ import annotations

from src.core.context import ConversationContext
from src.core.errors import TenantNotFoundError


class TenantMiddleware:
    """Resolves and attaches the TenantConfig to the ConversationContext."""

    async def before(self, ctx: ConversationContext) -> None:
        from src.customers.loader import get_tenant_config
        config = get_tenant_config(ctx.tenant_slug)
        if config is None:
            raise TenantNotFoundError(ctx.tenant_slug)
        ctx.tenant_config = config

    async def after(self, ctx: ConversationContext, reply_text: str) -> None:
        pass  # nothing to do after
