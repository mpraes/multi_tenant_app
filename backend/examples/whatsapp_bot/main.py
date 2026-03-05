"""
WhatsApp Bot via Twilio — exemplo de bootstrap para produção.

Este arquivo mostra como montar um servidor FastAPI mínimo
com apenas o canal WhatsApp ativado, sem o resto do stack.

Útil quando o cliente quer SOMENTE WhatsApp e você não quer
carregar os outros canais desnecessariamente.

Uso:
    cd backend
    uvicorn examples.whatsapp_bot.main:app --port 8000

Depois configure o webhook no painel Twilio:
    URL: https://<seu-host>/channels/whatsapp/<slug>
    Method: POST

Variáveis de ambiente necessárias:
    OPENAI_API_KEY
    TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN
    TWILIO_WHATSAPP_NUMBER
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.channels.whatsapp_twilio import router as whatsapp_router
from src.customers.loader import reload_tenants
from src.storage.database import init_db
from src.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    reload_tenants()
    yield


app = FastAPI(title="WhatsApp Bot", lifespan=lifespan)
app.include_router(whatsapp_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "channel": "whatsapp"}


# Para testar localmente com ngrok (expõe localhost para o Twilio):
#   1. ngrok http 8000
#   2. Copie a URL https://... gerada pelo ngrok
#   3. No painel Twilio → WhatsApp Sandbox → configure a URL do webhook
#   4. Envie uma mensagem no WhatsApp para o número sandbox
