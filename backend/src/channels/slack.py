"""
Slack channel adapter.

Como funciona:
  - Slack envia eventos via HTTP POST para o webhook (Event Subscriptions).
  - O primeiro POST é um challenge de verificação — responder com o challenge.
  - Mensagens reais chegam no evento 'app_mention' ou 'message'.
  - A resposta é enviada via Slack Web API (chat.postMessage).

Pré-requisitos:
  1. Criar Slack App em https://api.slack.com/apps
  2. Ativar Event Subscriptions → Request URL: https://<host>/channels/slack/<slug>
  3. Assinar eventos: app_mention (menção) e/ou message.im (DM)
  4. Instalar app no workspace e copiar Bot Token (xoxb-...)
  5. Definir SLACK_BOT_TOKEN e SLACK_SIGNING_SECRET no .env

Referência: https://api.slack.com/apis/events-api
"""

from __future__ import annotations

import hashlib
import hmac
import time

from fastapi import APIRouter, Header, HTTPException, Request

from src.channels.base import BaseChannel
from src.config.settings import settings
from src.core.message import Message, MessageChannel, Response
from src.core.orchestrator import Orchestrator
from src.utils.ids import new_session_id

router = APIRouter(prefix="/channels/slack", tags=["slack"])


@router.post("/{tenant_slug}")
async def slack_webhook(
    tenant_slug: str,
    request: Request,
    x_slack_signature: str = Header(default=""),
    x_slack_request_timestamp: str = Header(default=""),
) -> dict:
    """
    Recebe eventos do Slack e responde via Web API.

    Dois tipos de payload chegam neste endpoint:
      1. url_verification: challenge de verificação inicial (responder {"challenge": ...})
      2. event_callback:   evento real (mensagem, menção)

    Segurança: verificar assinatura HMAC antes de processar qualquer evento.
    Use _verify_slack_signature() abaixo — NUNCA pule esta verificação.

    Implementação pendente:
      - Verificar assinatura (_verify_slack_signature)
      - Checar body["type"] == "url_verification" → retornar challenge
      - Extrair event.text, event.user, event.channel do body
      - Ignorar mensagens do próprio bot (event.bot_id presente)
      - Chamar Orchestrator.process(message)
      - Enviar resposta via _post_message(channel, text)
    """
    body = await request.json()

    # Challenge de verificação (feito uma única vez na configuração do app)
    if body.get("type") == "url_verification":
        return {"challenge": body["challenge"]}

    # TODO: implementar processamento de eventos reais
    raise NotImplementedError("Slack adapter pendente de implementação.")


def _verify_slack_signature(
    body_bytes: bytes,
    timestamp: str,
    signature: str,
) -> bool:
    """
    Verifica se a requisição veio realmente do Slack.

    Algoritmo:
      1. Rejeitar se timestamp tiver mais de 5 minutos (replay attack)
      2. Construir string: "v0:{timestamp}:{body}"
      3. HMAC-SHA256 com SLACK_SIGNING_SECRET
      4. Comparar com signature (formato "v0=<hex>")

    Retorna False se a assinatura for inválida — neste caso, retorne HTTP 403.
    """
    if abs(time.time() - float(timestamp)) > 300:
        return False
    base = f"v0:{timestamp}:{body_bytes.decode()}"
    expected = "v0=" + hmac.new(
        settings.slack_signing_secret.encode(),
        base.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


async def _post_message(channel: str, text: str) -> None:
    """
    Envia uma mensagem para um canal ou DM do Slack via Web API.

    Para mensagens ricas (Block Kit), substitua 'text' por 'blocks'.
    Referência: https://api.slack.com/block-kit
    """
    import httpx
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {settings.slack_bot_token}"},
            json={"channel": channel, "text": text},
        )


class SlackChannel(BaseChannel):
    """Adapter Slack para uso fora do contexto HTTP."""

    @property
    def channel_id(self) -> MessageChannel:
        return MessageChannel.SLACK

    async def parse_incoming(self, raw: dict) -> Message:
        """
        Converte um Slack Event para Message.

        raw deve ser o objeto 'event' do payload:
            {"type": "app_mention", "user": "U123", "text": "<@BOT> olá", "channel": "C456"}

        Lembre de remover a menção ao bot do texto: re.sub(r"<@\w+>", "", text).strip()
        """
        raise NotImplementedError

    async def format_outgoing(self, response: Response) -> dict:
        """Formata Response para payload do chat.postMessage."""
        raise NotImplementedError

    async def send(self, payload: dict) -> None:
        await _post_message(payload["channel"], payload["text"])
