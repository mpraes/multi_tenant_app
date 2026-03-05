"""
FastAPI application entry point.

Startup sequence:
  1. Logging configured
  2. DB tables created (dev) or migrations applied (prod)
  3. Tenant registry loaded (cached from customers/)
  4. Routers mounted

Run locally:
    uvicorn src.main:app --reload --port 8000

Or via Docker:
    docker-compose up
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.channels.web_chat import router as web_chat_router
from src.config.settings import settings
from src.customers.loader import list_tenants, reload_tenants
from src.storage.database import init_db
from src.utils.logging import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle manager."""
    setup_logging()
    logger = get_logger("main")
    logger.info("Starting multi-tenant chatbot — env=%s", settings.app_env)

    # Initialise database (creates tables in dev; use Alembic in prod)
    await init_db()

    # Warm the tenant registry cache
    reload_tenants()
    tenants = list_tenants()
    logger.info("Loaded %d tenant(s): %s", len(tenants), [t.slug for t in tenants])

    yield  # app is running

    logger.info("Shutting down.")


app = FastAPI(
    title="Multi-Tenant Chatbot Framework",
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
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# ── Channel routers ───────────────────────────────────────────────────────────
app.include_router(web_chat_router)
# Uncomment as you integrate more channels:
# from src.channels.telegram import router as telegram_router
# app.include_router(telegram_router)
# from src.channels.whatsapp_twilio import router as whatsapp_router
# app.include_router(whatsapp_router)


@app.get("/health")
async def health() -> dict:
    """Simple health check — used by Docker/K8s liveness probes."""
    return {"status": "ok", "env": settings.app_env}


@app.get("/tenants")
async def tenants_list() -> list[dict]:
    """List registered tenants. Disable or protect this in production."""
    return [{"slug": t.slug, "name": t.name} for t in list_tenants()]
