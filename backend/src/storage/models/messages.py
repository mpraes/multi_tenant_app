"""Message persistence model — stores conversation history per session."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.models.base_model import Base


class MessageRecord(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(256), nullable=False)
    channel: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)   # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Store token counts for cost tracking per tenant
    input_tokens: Mapped[int] = mapped_column(default=0)
    output_tokens: Mapped[int] = mapped_column(default=0)
