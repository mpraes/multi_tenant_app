"""End-user model — one row per user per tenant."""

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.models.base_model import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        # Same user_id can exist on different tenants (e.g. same Telegram user ID)
        UniqueConstraint("tenant_slug", "external_id", name="uq_user_tenant_external"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(256), nullable=False)  # channel user ID
    channel: Mapped[str] = mapped_column(String(64), nullable=False)        # "telegram", "web_chat"
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
