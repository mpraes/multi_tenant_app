#!/usr/bin/env python3
"""
new_client.py — scaffold a new tenant in seconds.

Usage:
    python scripts/new_client.py <slug> "<Client Name>"

Example:
    python scripts/new_client.py initech "Initech LLC"

What it does:
  1. Creates backend/src/customers/<slug>/ with config.py, prompts.py, flows.py
  2. Copies and personalises the ACME template files
  3. Prints the next steps (env vars, channels, LLM settings)

After running:
  - Edit backend/src/customers/<slug>/config.py  → set channels, model, extras
  - Edit backend/src/customers/<slug>/prompts.py → write the system prompt
  - Edit backend/src/customers/<slug>/flows.py   → add keyword shortcuts
  - Add OPENAI_API_KEY (or client-specific key) to backend/.env
  - Restart the server — the loader will auto-detect the new package
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ── Template strings ──────────────────────────────────────────────────────────

CONFIG_TEMPLATE = '''\
"""
{name} — tenant configuration.

Consultant checklist:
  [ ] enabled_channels  — which channels the client uses
  [ ] llm_model         — gpt-4o-mini (cheap) vs gpt-4o (smarter)
  [ ] system_prompt_override in prompts.py
  [ ] flows             — keyword shortcuts specific to this client
  [ ] extra             — client-specific data (product IDs, URLs, etc.)
"""

from src.customers.{slug}.flows import FLOWS as {SLUG}_FLOWS
from src.customers.{slug}.prompts import SYSTEM_PROMPT
from src.customers.base import TenantConfig

CONFIG = TenantConfig(
    slug="{slug}",
    name="{name}",

    # ── Channels ──────────────────────────────────────────────────────────────
    enabled_channels=["web_chat"],   # add "telegram", "whatsapp", "slack" as needed

    # ── LLM ───────────────────────────────────────────────────────────────────
    llm_provider="openai",           # openai | azure_openai | ollama
    llm_model="gpt-4o-mini",         # upgrade to gpt-4o for complex flows
    llm_temperature=0.7,
    llm_max_tokens=512,

    # ── Prompts ───────────────────────────────────────────────────────────────
    system_prompt_override=SYSTEM_PROMPT,

    # ── Flows ─────────────────────────────────────────────────────────────────
    flows={SLUG}_FLOWS,

    # ── Feature flags ─────────────────────────────────────────────────────────
    rag_enabled=False,
    history_window=8,

    # ── Client-specific extras ─────────────────────────────────────────────
    extra={{
        "support_email": "support@{slug}.example.com",
        # Add client-specific values here (product IDs, webhook URLs, etc.)
    }},
)
'''

PROMPTS_TEMPLATE = '''\
"""
{name} — system prompt.

Tips for writing effective system prompts:
  - State the bot name and company in the first sentence.
  - Define tone: friendly? formal? technical?
  - List what the bot CAN help with (scope).
  - List what it CANNOT do (guard rails).
  - Add a fallback: "If you don\\'t know, offer to escalate."
  - Test with: what would embarrass the client if the bot said it?
"""

SYSTEM_PROMPT = """\\
You are the virtual assistant for {name}.

Persona: friendly, helpful, and professional.

Scope:
- Answer questions about {name}\\'s products and services.
- Guide users through common tasks and troubleshooting.

Out of scope:
- Do NOT discuss competitor products.
- Do NOT provide legal, medical, or financial advice.

If you cannot answer a question, say so clearly and offer to connect the user
with a human agent.

Always respond in the same language the user writes in.
"""
'''

FLOWS_TEMPLATE = '''\
"""
{name} — custom flow overrides.

Add keyword-triggered handlers specific to {name}.
These take priority over domain/flows.py for {slug} messages.

Pattern:
  FLOWS = {{"keyword": async_handler_function}}

The router matches if the keyword is found anywhere in the lowercased message.
"""

from __future__ import annotations

from src.core.context import ConversationContext


async def handle_greeting(ctx: ConversationContext) -> str:
    """Custom greeting for {name}. Remove this if the domain default is fine."""
    return "Hello! Welcome to {name}. How can I help you today?"


# ── Flow registry ─────────────────────────────────────────────────────────────
# Add more entries as you discover common intents for this client.
FLOWS: dict = {{
    # "keyword": handler_function,
    # Example:
    # "pricing": handle_pricing,
    # "demo": handle_demo,
}}
'''

INIT_TEMPLATE = '''\
"""Customer package for {name} (slug: {slug})."""
'''


# ── Helpers ───────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert arbitrary text to a safe slug (lowercase, underscores)."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s-]+", "_", slug).strip("_")
    return slug


def create_client(slug: str, name: str) -> None:
    root = Path(__file__).parent.parent / "backend" / "src" / "customers" / slug

    if root.exists():
        print(f"❌  Directory already exists: {root}")
        print("    Delete it or choose a different slug.")
        sys.exit(1)

    root.mkdir(parents=True)

    ctx = {"slug": slug, "name": name, "SLUG": slug.upper()}

    (root / "__init__.py").write_text(INIT_TEMPLATE.format(**ctx))
    (root / "config.py").write_text(CONFIG_TEMPLATE.format(**ctx))
    (root / "prompts.py").write_text(PROMPTS_TEMPLATE.format(**ctx))
    (root / "flows.py").write_text(FLOWS_TEMPLATE.format(**ctx))

    print(f"\n✅  Created customers/{slug}/ with 4 files.\n")
    print("Next steps:")
    print(f"  1. Edit backend/src/customers/{slug}/prompts.py  → write the system prompt")
    print(f"  2. Edit backend/src/customers/{slug}/config.py   → set channels, model, extras")
    print(f"  3. Edit backend/src/customers/{slug}/flows.py    → add keyword shortcuts")
    print( "  4. Ensure OPENAI_API_KEY (or the right provider key) is in backend/.env")
    print( "  5. Restart the server — the loader will pick it up automatically\n")
    print("Test it immediately (after server restart):")
    print(f'  curl -X POST http://localhost:8000/chat/{slug} \\')
    print( '    -H "Content-Type: application/json" \\')
    print( '    -d \'{"user_id": "test", "text": "hello"}\'\n')


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python scripts/new_client.py <slug> \"<Client Name>\"")
        print('Example: python scripts/new_client.py initech "Initech LLC"')
        sys.exit(1)

    raw_slug = sys.argv[1].strip().lower()
    name = sys.argv[2].strip()
    slug = slugify(raw_slug)

    if slug != raw_slug:
        print(f"⚠️   Slug normalised: '{raw_slug}' → '{slug}'")

    if not slug:
        print("❌  Slug cannot be empty.")
        sys.exit(1)

    print(f"Creating tenant: slug='{slug}' name='{name}'")
    create_client(slug, name)


if __name__ == "__main__":
    main()
