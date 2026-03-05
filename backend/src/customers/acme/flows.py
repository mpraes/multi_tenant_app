"""
ACME Corp — custom flow overrides.

Define keyword-triggered handlers that are specific to ACME.
These take priority over domain/flows.py for ACME messages.

Pattern:
  FLOWS = {"keyword": async_handler_function}

The router checks if the keyword appears anywhere in the lowercased message text.
Keep keywords specific enough to avoid false matches ("price" > "p").
"""

from __future__ import annotations

from src.core.context import ConversationContext


async def handle_demo_request(ctx: ConversationContext) -> str:
    """Triggered when the user asks about scheduling a demo."""
    name = ctx.state.get("user_display_name", "there")
    return (
        f"Hi {name}! I'd love to set up a demo for you. 🎯\n\n"
        "Please send your preferred date and time to sales@acme.example.com "
        "or fill out the form at https://acme.example.com/demo.\n\n"
        "A member of our team will confirm within 1 business day."
    )


async def handle_support(ctx: ConversationContext) -> str:
    """Triggered when the user mentions needing support or has an issue."""
    return (
        "I'm sorry to hear you're having trouble! Here's how to get help:\n\n"
        "• **Email:** support@acme.example.com\n"
        "• **Hours:** Mon–Fri, 9h–18h BRT\n\n"
        "Please describe your issue and include your account ID if you have one."
    )


# ── Flow registry ─────────────────────────────────────────────────────────────
# Add entries here for any ACME-specific shortcut you want.
FLOWS: dict = {
    "demo": handle_demo_request,
    "schedule": handle_demo_request,
    "support": handle_support,
    "issue": handle_support,
    "problem": handle_support,
    "broken": handle_support,
}
