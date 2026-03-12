"""
Anthropic provider — chama a API Messages diretamente via httpx.
Anthropic provider — calls the Messages API directly via httpx.

Variáveis de ambiente necessárias / Required env vars:
    ANTHROPIC_API_KEY
    ANTHROPIC_MODEL  (padrão / default: claude-sonnet-4-6)
"""

from __future__ import annotations

from src.llm.base import BaseLLMProvider, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    """
    Chama a API Anthropic Messages via httpx (sem SDK extra).
    Calls the Anthropic Messages API via httpx (no extra SDK needed).
    """

    _BASE_URL = "https://api.anthropic.com/v1/messages"
    _API_VERSION = "2023-06-01"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6") -> None:
        self._api_key = api_key
        self._model = model

    def model_name(self) -> str:
        return self._model

    async def chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """
        Envia a conversa para a API Anthropic e retorna a resposta normalizada.
        Sends the conversation to the Anthropic API and returns the normalised response.
        """
        import httpx

        # Anthropic exige papéis alternados e não aceita "system" na lista de mensagens
        # Anthropic requires alternating roles and doesn't accept "system" in the messages list
        payload = {
            "model": self._model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages,
        }

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": self._API_VERSION,
            "content-type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self._BASE_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        text = data["content"][0]["text"]
        usage = data.get("usage", {})

        return LLMResponse(
            text=text,
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            model=self._model,
        )
