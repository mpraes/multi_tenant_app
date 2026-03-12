"""
AWS Bedrock provider — chama modelos via boto3.
AWS Bedrock provider — calls models via boto3.

Dependência extra necessária / Extra dependency required:
    cd backend && uv add boto3

Variáveis de ambiente necessárias / Required env vars:
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_REGION          (padrão / default: us-east-1)
    BEDROCK_MODEL_ID    (padrão / default: anthropic.claude-3-5-sonnet-20241022-v2:0)
"""

from __future__ import annotations

import json

from src.llm.base import BaseLLMProvider, LLMResponse


class BedrockProvider(BaseLLMProvider):
    """
    Chama a AWS Bedrock Converse API via boto3.
    Calls the AWS Bedrock Converse API via boto3.
    """

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region: str = "us-east-1",
        model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
    ) -> None:
        self._model_id = model_id
        try:
            import boto3
        except ImportError as exc:
            raise ImportError(
                "boto3 não está instalado. Execute: cd backend && uv add boto3\n"
                "boto3 is not installed. Run: cd backend && uv add boto3"
            ) from exc

        # Usa a Converse API unificada (disponível para todos os provedores Bedrock)
        # Uses the unified Converse API (available across all Bedrock model providers)
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def model_name(self) -> str:
        return self._model_id

    async def chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """
        Envia a conversa para o Bedrock via Converse API e retorna a resposta normalizada.
        Sends the conversation to Bedrock via Converse API and returns the normalised response.
        """
        import asyncio

        # Converte mensagens para o formato Converse API
        # Converts messages to Converse API format
        converse_messages = [
            {"role": m["role"], "content": [{"text": m["content"]}]}
            for m in messages
        ]

        # boto3 é síncrono — executa em thread pool para não bloquear o event loop
        # boto3 is synchronous — run in thread pool to avoid blocking the event loop
        response = await asyncio.to_thread(
            self._client.converse,
            modelId=self._model_id,
            system=[{"text": system_prompt}],
            messages=converse_messages,
            inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
        )

        text = response["output"]["message"]["content"][0]["text"]
        usage = response.get("usage", {})

        return LLMResponse(
            text=text,
            input_tokens=usage.get("inputTokens", 0),
            output_tokens=usage.get("outputTokens", 0),
            model=self._model_id,
        )
