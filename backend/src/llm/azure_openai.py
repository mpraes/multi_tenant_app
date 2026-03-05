"""Azure OpenAI provider adapter."""

from __future__ import annotations

from src.llm.base import BaseLLMProvider, LLMResponse


class AzureOpenAIProvider(BaseLLMProvider):
    """
    Calls Azure OpenAI via the openai SDK (azure mode).

    Configuration:
        AZURE_OPENAI_API_KEY
        AZURE_OPENAI_ENDPOINT     https://<resource>.openai.azure.com/
        AZURE_OPENAI_DEPLOYMENT   your deployment name
        AZURE_OPENAI_API_VERSION  e.g. 2024-02-01
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        deployment: str,
        api_version: str = "2024-02-01",
    ) -> None:
        self._deployment = deployment
        import openai
        self._client = openai.AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
        )

    def model_name(self) -> str:
        return f"azure/{self._deployment}"

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
            model=self._deployment,
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
            model=self.model_name(),
        )
