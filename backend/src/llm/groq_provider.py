"""
Groq provider — API compatível com OpenAI, usa o mesmo SDK.
Groq provider — OpenAI-compatible API, reuses the same SDK.

Variáveis de ambiente necessárias / Required env vars:
    GROQ_API_KEY
    GROQ_MODEL  (padrão / default: llama-3.3-70b-versatile)
"""

from __future__ import annotations

from src.llm.base import BaseLLMProvider, LLMResponse


class GroqProvider(BaseLLMProvider):
    """
    Chama a API do Groq via endpoint compatível com OpenAI.
    Calls the Groq API via its OpenAI-compatible endpoint.
    """

    _BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile") -> None:
        self._model = model
        # Reutiliza AsyncOpenAI apontando para o endpoint do Groq
        # Reuses AsyncOpenAI pointing at the Groq endpoint
        import openai
        self._client = openai.AsyncOpenAI(api_key=api_key, base_url=self._BASE_URL)

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
        Envia a conversa para o Groq e retorna a resposta normalizada.
        Sends the conversation to Groq and returns the normalised response.
        """
        full_messages = [{"role": "system", "content": system_prompt}, *messages]

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=full_messages,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
        )

        choice = response.choices[0]
        usage = response.usage

        return LLMResponse(
            text=choice.message.content or "",
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            model=self._model,
        )
