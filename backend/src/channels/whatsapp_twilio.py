"""
WhatsApp channel adapter via Twilio.

Como funciona:
  - Twilio recebe mensagens do WhatsApp e faz POST no seu webhook.
  - Este adapter decodifica o form-data do Twilio, processa e responde
    com TwiML (XML) que o Twilio usa para enviar a resposta ao usuário.

Pré-requisitos:
  1. Conta Twilio com WhatsApp aprovado (ou usar Sandbox para testes)
  2. Definir TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER no .env
  3. No painel Twilio → Messaging → WhatsApp → configurar webhook:
       URL: https://<host>/channels/whatsapp/<slug>
       Method: POST

Sandbox para testes (sem aprovação prévia):
  - Twilio Console → Messaging → Try it out → Send a WhatsApp message
  - Número sandbox: whatsapp:+14155238886

Referência: https://www.twilio.com/docs/whatsapp/api
"""

from __future__ import annotations

from fastapi import APIRouter, Form, Response as FastAPIResponse
from fastapi.responses import PlainTextResponse

from src.channels.base import BaseChannel
from src.core.message import Message, MessageChannel, Response
from src.core.orchestrator import Orchestrator
from src.utils.ids import new_session_id

router = APIRouter(prefix="/channels/whatsapp", tags=["whatsapp"])


@router.post("/{tenant_slug}", response_class=PlainTextResponse)
async def whatsapp_webhook(
    tenant_slug: str,
    Body: str = Form(...),        # texto da mensagem (campo Twilio)
    From: str = Form(...),        # remetente: "whatsapp:+5511999999999"
    To: str = Form(...),          # número do bot
    MessageSid: str = Form(...),  # ID único da mensagem no Twilio
) -> str:
    """
    Recebe mensagens WhatsApp via Twilio e responde com TwiML.

    O Twilio espera uma resposta TwiML com <Response><Message>texto</Message></Response>.
    Se o processamento demorar >15s, use status callback e responda de forma assíncrona.

    Implementação pendente:
      - Construir Message com user_id=From, session_id baseado no From+tenant
      - Chamar Orchestrator.process(message)
      - Retornar TwiML com a resposta
    """
    # TODO: implementar lógica de processamento
    # Exemplo de resposta TwiML:
    # <?xml version="1.0" encoding="UTF-8"?>
    # <Response><Message>Olá! Como posso ajudar?</Message></Response>
    raise NotImplementedError("WhatsApp adapter pendente de implementação.")


def _build_twiml_response(text: str) -> str:
    """
    Gera a resposta TwiML para envio pelo Twilio.

    Para mensagens longas ou com mídia, consulte:
    https://www.twilio.com/docs/messaging/twiml
    """
    # Escapar caracteres XML especiais no text antes de usar em produção
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{text}</Message></Response>"
    )


class WhatsAppTwilioChannel(BaseChannel):
    """
    Adapter WhatsApp/Twilio para uso fora do contexto HTTP (ex: envio proativo).

    Para envio ativo (notificações, alertas), use a API REST do Twilio diretamente:
        client.messages.create(from_=bot_number, to=user_number, body=text)
    """

    @property
    def channel_id(self) -> MessageChannel:
        return MessageChannel.WHATSAPP

    async def parse_incoming(self, raw: dict) -> Message:
        """
        Converte form-data do Twilio para Message.

        raw deve conter: Body, From, To, MessageSid
        session_id = hash do número do usuário (conversa é 1:1 no WhatsApp)
        """
        # TODO: extrair campos e construir Message
        raise NotImplementedError

    async def format_outgoing(self, response: Response) -> dict:
        """Prepara payload para envio proativo via Twilio REST API."""
        # TODO: retornar dict com from_, to, body
        raise NotImplementedError

    async def send(self, payload: dict) -> None:
        """
        Envia mensagem via Twilio REST API (para envio proativo).

        Requer: pip install twilio
        """
        # TODO: instanciar Client do Twilio e chamar messages.create(...)
        raise NotImplementedError
