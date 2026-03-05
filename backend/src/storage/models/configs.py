"""
TenantConfig DB model — stores per-tenant settings that can be edited at runtime.

This complements the code-level config in customers/<slug>/config.py.
Use this table for values that ops/clients may need to change without a redeploy
(e.g. toggling a feature flag, updating a webhook URL, rotating an API key).
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.models.base_model import Base


class TenantConfigRecord(Base):
    __tablename__ = "tenant_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    tenant_name: Mapped[str] = mapped_column(String(256), nullable=False)
    # JSON blob for flexible per-tenant settings — avoids schema migrations for new flags
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
