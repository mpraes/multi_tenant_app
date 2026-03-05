"""Abstract base interface for all LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Normalised response from any provider."""
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""


class BaseLLMProvider(ABC):
    """
    Contract that every LLM provider adapter must satisfy.

    To add a new provider (e.g. Anthropic, Gemini):
      1. Create src/llm/anthropic_provider.py
      2. Subclass BaseLLMProvider and implement .chat()
      3. Register the slug in src/llm/__init__.py  get_llm_provider()
    """

    @abstractmethod
    async def chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],  # [{"role": "user"|"assistant", "content": "..."}]
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Send a chat request and return the normalised response."""

    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier for logging/billing."""
