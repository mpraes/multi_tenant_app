"""
Domain base system prompt — shared by all tenants that don't override it.

This is the generic fallback. In practice, every production client should
provide a system_prompt_override in their customers/<slug>/prompts.py.

Think of this as the "blank slate" that works without any client context.
"""

BASE_SYSTEM_PROMPT = """\
You are a helpful AI assistant. Answer the user's questions clearly and concisely.

If you don't know the answer to something, say so honestly rather than guessing.
Always be polite and professional.

Respond in the same language the user writes in.
"""
