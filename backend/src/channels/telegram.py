"""
Telegram channel adapter.

Como funciona:
  - O Telegram envia eventos para o webhook via POST.
  - Este adapter normaliza o payload para um Message e devolve a resposta
    chamando a API do Telegram (sendMessage).

Pré-requisitos:
  1. Criar o bot no BotFather e obter o token
  2. Definir TELEGRAM_BOT_TOKEN no .env
  3. Registrar o webhook após o deploy:
       curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<host>/channels/telegram/<slug>"

Referência: https://core.telegram.org/bots/api
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Request

from src.channels.base import BaseChannel
from src.config.settings import settings
from src.core.message import Message, MessageChannel, Response
from src.core.orchestrator import Orchestrator
from src.utils.ids import new_session_id

router = APIRouter(prefix="/channels/telegram", tags=["telegram"])

_TELEGRAM_API = "https://api.telegram.org/bot"


@router.post("/{tenant_slug}")
async def telegram_webhook(tenant_slug: str, request: Request) -> dict:
    """
    Recebe eventos do Telegram e responde na mesma conversa.

    O Telegram espera HTTP 200 com body vazio ou {"ok": true} em até 5s.
    Se demorar mais, ele reprocessa o evento — use filas para processamento lento.

    Implementação pendente:
      - Extrair update_id, chat.id, text do body (await request.json())
      - Construir Message com user_id=str(chat.id), session_id baseado no chat_id
      - Chamar Orchestrator.process(message)
      - Enviar resposta via _send_message(chat_id, response.text)
      - Retornar {"ok": True}
    """
    body = await request.json()
    # TODO: implementar parsing do payload Telegram
    # Estrutura típica do body:
    # {
    #   "update_id": 123,
    #   "message": {
    #     "chat": {"id": 456, "type": "private"},
    #     "from": {"id": 456, "first_name": "João"},
    #     "text": "olá"
    #   }
    # }
    raise NotImplementedError("Telegram adapter pendente de implementação.")


async def _send_message(chat_id: int, text: str) -> None:
    """
    Envia uma mensagem para um chat do Telegram via API REST.

    Suporta Markdown (parse_mode="Markdown") — use ** para negrito, _ para itálico.
    Para mensagens longas (>4096 chars), divida em chunks antes de enviar.
    """
    url = f"{_TELEGRAM_API}{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
        })


class TelegramChannel(BaseChannel):
    """
    Adapter do Telegram para uso fora do contexto HTTP (ex: testes, scripts).

    Para usar no webhook HTTP, use o router acima diretamente.
    Esta classe é útil para envio proativo de mensagens (notificações).
    """

    @property
    def channel_id(self) -> MessageChannel:
        return MessageChannel.TELEGRAM

    async def parse_incoming(self, raw: dict) -> Message:
        """
        Converte um Telegram Update para Message.

        raw deve ser o objeto 'message' do Update:
            {"chat": {"id": 123}, "from": {"id": 123}, "text": "..."}
        """
        # TODO: extrair campos do raw Telegram Update
        raise NotImplementedError

    async def format_outgoing(self, response: Response) -> dict:
        """Formata Response para o payload da API sendMessage do Telegram."""
        # TODO: mapear response.text para Telegram message payload
        raise NotImplementedError

    async def send(self, payload: dict) -> None:
        """Envia o payload via _send_message."""
        await _send_message(payload["chat_id"], payload["text"])
