"""
Ponto de entrada da aplicação FastAPI.
FastAPI application entry point.

Sequência de startup / Startup sequence:
  1. Logging configurado / Logging configured
  2. Tabelas do banco criadas (dev) ou migrações aplicadas (prod) / DB tables created or migrations applied
  3. Routers montados / Routers mounted

Rodar localmente / Run locally:
    uvicorn src.main:app --reload --port 8000

Ou via Docker / Or via Docker:
    docker-compose up
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.main_api import router as api_router
from src.channels.web_chat import router as web_chat_router
from src.config.settings import CONFIG, settings
from src.storage.database import init_db
from src.utils.logging import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida startup/shutdown.
    Startup / shutdown lifecycle manager.
    """
    setup_logging()
    logger = get_logger("main")
    logger.info("Iniciando chatbot '%s' — env=%s / Starting chatbot '%s' — env=%s",
                CONFIG.name, settings.app_env, CONFIG.name, settings.app_env)

    # Inicializa o banco (cria tabelas em dev; use Alembic em prod)
    # Initialise database (creates tables in dev; use Alembic in prod)
    await init_db()

    yield  # app rodando / app is running

    logger.info("Encerrando. / Shutting down.")


app = FastAPI(
    title=CONFIG.name,
    version="0.1.0",
    lifespan=lifespan,
    # Disable docs in production to avoid leaking internals
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
)

# CORS — tighten origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else [],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ── Channel routers ───────────────────────────────────────────────────────────
app.include_router(web_chat_router)
app.include_router(api_router)
# Uncomment as you integrate more channels:
# from src.channels.telegram import router as telegram_router
# app.include_router(telegram_router)
# from src.channels.whatsapp_twilio import router as whatsapp_router
# app.include_router(whatsapp_router)


@app.get("/health")
async def health() -> dict:
    """
    Health check para probes do Docker/K8s.
    Liveness probe for Docker/K8s.
    """
    return {"status": "ok", "env": settings.app_env}
