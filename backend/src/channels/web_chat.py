"""
Web chat channel adapter + FastAPI router.

This is the simplest channel to test locally — no external webhooks needed.

Endpoint:  POST /chat/{tenant_slug}
Payload:   {"user_id": "...", "session_id": "...", "text": "..."}
Response:  {"text": "...", "session_id": "..."}
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.channels.base import BaseChannel
from src.core.message import Message, MessageChannel, Response
from src.core.orchestrator import Orchestrator
from src.utils.ids import new_session_id

router = APIRouter(prefix="/chat", tags=["web_chat"])


class ChatRequest(BaseModel):
    user_id: str
    text: str
    session_id: str = ""   # auto-generated if empty


class ChatResponse(BaseModel):
    text: str
    session_id: str


@router.post("/{tenant_slug}", response_model=ChatResponse)
async def chat(tenant_slug: str, body: ChatRequest) -> ChatResponse:
    """Main web chat endpoint. One request = one conversational turn."""
    session_id = body.session_id or new_session_id()

    message = Message(
        tenant_slug=tenant_slug,
        session_id=session_id,
        user_id=body.user_id,
        text=body.text,
        channel=MessageChannel.WEB_CHAT,
    )

    try:
        orchestrator = Orchestrator()
        response: Response = await orchestrator.process(message)
    except Exception as exc:
        # Surface errors cleanly — replace with proper error handling per client
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ChatResponse(text=response.text, session_id=response.session_id)


# ── Channel adapter class (for use outside HTTP context e.g. tests) ──────────

class WebChatChannel(BaseChannel):
    @property
    def channel_id(self) -> MessageChannel:
        return MessageChannel.WEB_CHAT

    async def parse_incoming(self, raw: dict) -> Message:
        return Message(
            tenant_slug=raw["tenant_slug"],
            session_id=raw.get("session_id") or new_session_id(),
            user_id=raw["user_id"],
            text=raw["text"],
            channel=MessageChannel.WEB_CHAT,
        )

    async def format_outgoing(self, response: Response) -> dict:
        return {"text": response.text, "session_id": response.session_id}

    async def send(self, payload: dict) -> None:
        # Web chat is request-response — payload is returned in the HTTP response
        pass
