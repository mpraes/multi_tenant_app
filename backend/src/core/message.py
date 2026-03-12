"""
Tipos de mensagem e evento compartilhados entre canais e a engine.
Shared message/event types used across channels and the engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageChannel(str, Enum):
    """Supported input channels. Add new ones as you integrate them."""
    WEB_CHAT = "web_chat"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SLACK = "slack"
    CONSOLE = "console"   # useful for local smoke-testing


@dataclass
class Message:
    """
    Canonical message unit flowing through the engine.

    All channels must normalise their native event into this structure
    before passing it to the engine. The engine never speaks directly
    to channel types — only to Message objects.
    """
    session_id: str          # identificador da conversa / conversation identifier
    user_id: str             # id do usuário no canal / end-user id (channel-specific)
    text: str                # conteúdo de texto / raw text content
    channel: MessageChannel  # canal de origem / origin channel
    role: MessageRole = MessageRole.USER
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)  # channel extras


@dataclass
class Response:
    """
    The engine output, consumed by the channel adapter for sending.

    Each channel adapter reads .text and optionally .metadata to build
    the channel-native payload (e.g. Slack Block Kit, WhatsApp template).
    """
    text: str
    session_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationTurn:
    """A single exchange stored in conversation history."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
