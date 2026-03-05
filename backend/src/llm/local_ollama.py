"""Local Ollama provider adapter — zero cost, fully offline."""

from __future__ import annotations

import httpx

from src.llm.base import BaseLLMProvider, LLMResponse


class OllamaProvider(BaseLLMProvider):
    """
    Calls a local Ollama instance via its REST API.

    Configuration:
        OLLAMA_BASE_URL  (default: http://localhost:11434)
        OLLAMA_MODEL     (default: llama3.2)

    Run locally:
        docker run -d -p 11434:11434 ollama/ollama
        ollama pull llama3.2
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2") -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    def model_name(self) -> str:
        return f"ollama/{self._model}"

    async def chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        full_messages = [{"role": "system", "content": system_prompt}, *messages]

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": full_messages,
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                },
            )
            resp.raise_for_status()
            data = resp.json()

        return LLMResponse(
            text=data["message"]["content"],
            model=self._model,
        )
