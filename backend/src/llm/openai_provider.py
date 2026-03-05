"""OpenAI provider adapter — works with OpenAI and any OpenAI-compatible API."""

from __future__ import annotations

from src.llm.base import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """
    Calls the OpenAI Chat Completions API.

    Configuration (via environment or tenant override):
        OPENAI_API_KEY
        OPENAI_MODEL  (default: gpt-4o-mini)
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._api_key = api_key
        self._model = model
        # Lazy import — only needed if this provider is active
        import openai
        self._client = openai.AsyncOpenAI(api_key=api_key)

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
