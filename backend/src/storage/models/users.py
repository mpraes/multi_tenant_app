"""
Modelo de usuário final — um registro por usuário/canal.
End-user model — one row per user per channel.
"""

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.models.base_model import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        # Mesmo external_id pode existir em canais diferentes / Same external_id can exist across channels
        UniqueConstraint("external_id", "channel", name="uq_user_external_channel"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(256), nullable=False)  # id no canal / channel user ID
    channel: Mapped[str] = mapped_column(String(64), nullable=False)        # "telegram", "web_chat"
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
