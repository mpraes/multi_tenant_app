"""Conversation context and state container for a single session."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.message import ConversationTurn, Message, MessageRole


@dataclass
class ConversationContext:
    """
    Holds the full state for one conversation turn.

    Created fresh on every incoming message and passed through the
    entire middleware + engine pipeline. Add fields here for anything
    that needs to travel alongside a message (user profile, retrieved
    RAG chunks, slot values, etc.).
    """
    message: Message
    history: list[ConversationTurn] = field(default_factory=list)
    # Contexto recuperado pelo RAG (se habilitado) / Context retrieved by RAG (if enabled)
    retrieved_context: str = ""
    # Bag livre para dados de middleware/fluxo / Arbitrary bag for middleware/flow data
    state: dict[str, Any] = field(default_factory=dict)

    @property
    def config(self):
        """
        Configuração do bot para esta instância.
        Bot configuration for this instance.
        """
        from src.config.settings import CONFIG
        return CONFIG

    def add_turn(self, role: MessageRole, content: str) -> None:
        self.history.append(ConversationTurn(role=role, content=content))

    def history_as_openai_messages(self) -> list[dict[str, str]]:
        """
        Formats conversation history for the OpenAI chat completion API.
        Prepend the system prompt before calling the LLM.
        """
        return [{"role": t.role.value, "content": t.content} for t in self.history]
