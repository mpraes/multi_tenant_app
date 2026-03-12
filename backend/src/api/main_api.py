"""
API router com endpoints comuns de gerenciamento do chatbot.
API router with common chatbot management endpoints.

Cobre / Covers:
  - Histórico de sessão  / Session history
  - Exclusão de sessão   / Session deletion
  - Feedback de mensagem / Message feedback
  - Upsert de usuário    / User upsert
  - Configuração do bot  / Bot config
  - Estatísticas de uso  / Usage stats

Montar em main.py / Mount in main.py:
    from src.api.main_api import router as api_router
    app.include_router(api_router)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select

from src.storage.database import async_session
from src.storage.models.messages import MessageRecord
from src.storage.models.users import User

router = APIRouter(prefix="/api", tags=["api"])


# ── Schemas / Esquemas ────────────────────────────────────────────────────────

class MessageOut(BaseModel):
    """Mensagem individual de uma conversa. / Single message in a conversation turn."""
    role: str
    content: str
    channel: str


class SessionSummary(BaseModel):
    """Informações resumidas de uma sessão. / Lightweight session info for listing."""
    session_id: str
    message_count: int


class FeedbackIn(BaseModel):
    """Payload para envio de feedback. / Payload for submitting message feedback."""
    message_id: int
    rating: int   # 1 = positivo / positive, -1 = negativo / negative
    comment: str = ""


class FeedbackOut(BaseModel):
    ok: bool
    message_id: int


class UserIn(BaseModel):
    """Payload para criar ou atualizar um usuário. / Payload to create or update a user."""
    external_id: str
    channel: str
    display_name: str | None = None


class UserOut(BaseModel):
    id: int
    external_id: str
    channel: str
    display_name: str | None


class BotConfigOut(BaseModel):
    """Configuração pública do bot. / Public bot configuration."""
    name: str
    system_prompt: str | None
    llm_provider: str | None
    llm_model: str | None
    llm_temperature: float
    llm_max_tokens: int
    rag_enabled: bool
    history_window: int


class BotConfigUpdateIn(BaseModel):
    """Campos editáveis do bot (todos opcionais). / Editable bot fields (all optional)."""
    name: str | None = None
    system_prompt: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_temperature: float | None = None
    llm_max_tokens: int | None = None
    rag_enabled: bool | None = None
    history_window: int | None = None


class UsageStats(BaseModel):
    """Uso agregado de tokens/mensagens. / Aggregate token/message usage."""
    total_messages: int
    total_input_tokens: int
    total_output_tokens: int
    unique_sessions: int
    unique_users: int


# ── Histórico de sessão / Session history ────────────────────────────────────

@router.get("/history/{session_id}", response_model=list[MessageOut])
async def get_session_history(session_id: str) -> list[MessageOut]:
    """
    Retorna todas as mensagens de uma sessão, ordenadas por inserção.
    Return all messages for a given session, ordered by insertion.
    """
    async with async_session() as db:
        result = await db.execute(
            select(MessageRecord)
            .where(MessageRecord.session_id == session_id)
            .order_by(MessageRecord.id)
        )
        records = result.scalars().all()

    if not records:
        raise HTTPException(status_code=404, detail="Sessão não encontrada / Session not found")

    return [MessageOut(role=r.role, content=r.content, channel=r.channel) for r in records]


# ── Listagem de sessões / Session list ────────────────────────────────────────

@router.get("/sessions/{user_id}", response_model=list[SessionSummary])
async def list_user_sessions(user_id: str) -> list[SessionSummary]:
    """
    Lista todas as sessões de um usuário, com contagem de mensagens.
    List all sessions for a user, with message count per session.
    """
    async with async_session() as db:
        result = await db.execute(
            select(MessageRecord.session_id, func.count(MessageRecord.id).label("cnt"))
            .where(MessageRecord.user_id == user_id)
            .group_by(MessageRecord.session_id)
        )
        rows = result.all()

    return [SessionSummary(session_id=row.session_id, message_count=row.cnt) for row in rows]


# ── Exclusão de sessão / Session deletion ────────────────────────────────────

@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str) -> None:
    """
    Exclui todas as mensagens de uma sessão (ex: solicitação de exclusão de dados).
    Delete all messages for a session (e.g. user requests data erasure).
    """
    async with async_session() as db:
        result = await db.execute(
            select(MessageRecord).where(MessageRecord.session_id == session_id)
        )
        records = result.scalars().all()

        if not records:
            raise HTTPException(status_code=404, detail="Sessão não encontrada / Session not found")

        for record in records:
            await db.delete(record)

        await db.commit()


# ── Feedback / Feedback ───────────────────────────────────────────────────────

@router.post("/feedback", response_model=FeedbackOut)
async def submit_feedback(body: FeedbackIn) -> FeedbackOut:
    """
    Armazena feedback positivo/negativo para uma mensagem.
    Store thumbs-up / thumbs-down feedback for a message.

    NOTA: para produção, crie uma tabela Feedback separada com coluna rating indexada.
    NOTE: for production, create a dedicated Feedback table with an indexed rating column.
    """
    if body.rating not in (1, -1):
        raise HTTPException(status_code=422, detail="rating deve ser 1 ou -1 / rating must be 1 or -1")

    async with async_session() as db:
        record = await db.get(MessageRecord, body.message_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Mensagem não encontrada / Message not found")

        await db.commit()

    return FeedbackOut(ok=True, message_id=body.message_id)


# ── Usuários / Users ──────────────────────────────────────────────────────────

@router.put("/users", response_model=UserOut)
async def upsert_user(body: UserIn) -> UserOut:
    """
    Cria ou atualiza o registro de um usuário.
    Create or update a user record.
    """
    async with async_session() as db:
        result = await db.execute(
            select(User).where(
                User.external_id == body.external_id,
                User.channel == body.channel,
            )
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                external_id=body.external_id,
                channel=body.channel,
                display_name=body.display_name,
            )
            db.add(user)
        else:
            # Atualiza nome se fornecido / Update display name if provided
            if body.display_name is not None:
                user.display_name = body.display_name

        await db.commit()
        await db.refresh(user)

    return UserOut(
        id=user.id,
        external_id=user.external_id,
        channel=user.channel,
        display_name=user.display_name,
    )


# ── Configuração do bot / Bot config ─────────────────────────────────────────

def _config_to_out(cfg) -> BotConfigOut:
    """Converte BotConfig para o schema de resposta. / Converts BotConfig to response schema."""
    return BotConfigOut(
        name=cfg.name,
        system_prompt=cfg.system_prompt,
        llm_provider=cfg.llm_provider,
        llm_model=cfg.llm_model,
        llm_temperature=cfg.llm_temperature,
        llm_max_tokens=cfg.llm_max_tokens,
        rag_enabled=cfg.rag_enabled,
        history_window=cfg.history_window,
    )


@router.get("/config", response_model=BotConfigOut)
async def get_bot_config() -> BotConfigOut:
    """
    Retorna a configuração pública do bot (sem segredos).
    Return public bot configuration (no secrets).
    """
    from src.config.settings import CONFIG
    return _config_to_out(CONFIG)


@router.put("/config", response_model=BotConfigOut)
async def update_bot_config(body: BotConfigUpdateIn) -> BotConfigOut:
    """
    Atualiza campos do bot e persiste em config.json.
    Update bot fields and persist to config.json.
    """
    import json as _json
    from src.config.settings import CONFIG, CONFIG_PATH, _PERSISTABLE

    # Carrega overrides existentes ou começa vazio
    # Load existing overrides or start fresh
    overrides: dict = {}
    if CONFIG_PATH.exists():
        overrides = _json.loads(CONFIG_PATH.read_text())

    # Aplica apenas os campos enviados / Apply only provided fields
    updates = body.model_dump(exclude_none=True)
    overrides.update(updates)

    # Persiste / Persist
    CONFIG_PATH.write_text(_json.dumps(overrides, indent=2, ensure_ascii=False))

    # Atualiza CONFIG em memória / Update in-memory CONFIG
    for k, v in updates.items():
        if k in _PERSISTABLE:
            setattr(CONFIG, k, v)

    return _config_to_out(CONFIG)


@router.delete("/config", status_code=204)
async def reset_bot_config() -> None:
    """
    Remove config.json, voltando aos defaults definidos em settings.py.
    Delete config.json, reverting to defaults defined in settings.py.
    """
    import dataclasses
    from src.config.settings import CONFIG, CONFIG_PATH, _PERSISTABLE

    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()

    # Reseta campos para os defaults do dataclass / Reset fields to dataclass defaults
    for f in dataclasses.fields(CONFIG):
        if f.name not in _PERSISTABLE:
            continue
        if f.default is not dataclasses.MISSING:
            setattr(CONFIG, f.name, f.default)
        elif f.default_factory is not dataclasses.MISSING:  # type: ignore[misc]
            setattr(CONFIG, f.name, f.default_factory())  # type: ignore[misc]


# ── Estatísticas de uso / Usage stats ────────────────────────────────────────

@router.get("/stats", response_model=UsageStats)
async def usage_stats() -> UsageStats:
    """
    Métricas de uso agregadas (mensagens, tokens, sessões, usuários).
    Aggregate usage metrics (messages, tokens, sessions, users).
    """
    async with async_session() as db:
        result = await db.execute(
            select(
                func.count(MessageRecord.id).label("total_messages"),
                func.sum(MessageRecord.input_tokens).label("input_tokens"),
                func.sum(MessageRecord.output_tokens).label("output_tokens"),
                func.count(func.distinct(MessageRecord.session_id)).label("unique_sessions"),
                func.count(func.distinct(MessageRecord.user_id)).label("unique_users"),
            )
        )
        row = result.one()

    return UsageStats(
        total_messages=row.total_messages or 0,
        total_input_tokens=row.input_tokens or 0,
        total_output_tokens=row.output_tokens or 0,
        unique_sessions=row.unique_sessions or 0,
        unique_users=row.unique_users or 0,
    )
