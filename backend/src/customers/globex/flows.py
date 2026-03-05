"""Globex Corp — custom flow overrides."""

from __future__ import annotations

from src.core.context import ConversationContext


async def handle_api_docs(ctx: ConversationContext) -> str:
    return (
        "You can find the full Globex API reference here:\n"
        "📄 https://docs.globex.example.com/api\n\n"
        "Need a specific endpoint or code example? Just ask!"
    )


async def handle_sla(ctx: ConversationContext) -> str:
    return (
        "Globex SLA summary for Enterprise tier:\n"
        "• **Uptime guarantee:** 99.9% monthly\n"
        "• **P1 response time:** < 1 hour\n"
        "• **Scheduled maintenance:** Sundays 02h–04h UTC\n\n"
        "For the full SLA document, contact your account manager."
    )


FLOWS: dict = {
    "api": handle_api_docs,
    "documentation": handle_api_docs,
    "docs": handle_api_docs,
    "sla": handle_sla,
    "uptime": handle_sla,
}
