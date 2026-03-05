"""
Domain-level flow registry — default keyword → handler mappings.

These apply to ALL tenants unless overridden in customers/<slug>/flows.py.
Keep this list minimal: only truly universal behaviours belong here.
"""

from src.domain.handlers import greeting, llm_reply

# Maps keyword (substring match in lowercased message) → async handler
FLOWS: dict = {
    "hello": greeting,
    "hi": greeting,
    "hey": greeting,
    "oi": greeting,      # Portuguese
    "olá": greeting,
    "help": llm_reply,   # "help" gets the full LLM treatment (not a fixed reply)
}
