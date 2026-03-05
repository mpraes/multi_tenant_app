"""
Orchestrator — top-level entry point called by channel adapters.

Channels call Orchestrator.process(message) and get a Response back.
The orchestrator owns: context creation, engine execution, and response packaging.
"""

from __future__ import annotations

from src.core.context import ConversationContext
from src.core.engine import Engine
from src.core.message import Message, Response


class Orchestrator:
    """
    Thin coordinator between channels and the engine.

    Keeps channels ignorant of engine internals, and keeps the engine
    ignorant of HTTP/channel concerns.
    """

    def __init__(self) -> None:
        self._engine = Engine()

    async def process(self, message: Message) -> Response:
        """
        Accept a normalised Message, run the pipeline, return a Response.

        This is the single method every channel adapter calls.
        """
        ctx = ConversationContext(message=message)
        reply_text = await self._engine.process(ctx)

        return Response(
            text=reply_text,
            session_id=message.session_id,
            tenant_slug=message.tenant_slug,
        )
