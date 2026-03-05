"""
Tenant provisioning — creates the DB record for a new client.

Called by scripts/new_client.py after the code scaffold is created.
Also useful for automated onboarding flows.
"""

from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.models.configs import TenantConfigRecord
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def provision_tenant(
    db: AsyncSession,
    slug: str,
    name: str,
    initial_config: dict | None = None,
) -> TenantConfigRecord:
    """
    Insert a new tenant row. Safe to call multiple times (upsert by slug).

    Args:
        db:             Active async DB session
        slug:           URL-safe identifier, e.g. "acme"
        name:           Human-readable name, e.g. "ACME Corp"
        initial_config: Optional JSON-serialisable config dict
    """
    from sqlalchemy import select

    existing = await db.execute(
        select(TenantConfigRecord).where(TenantConfigRecord.tenant_slug == slug)
    )
    record = existing.scalar_one_or_none()

    if record:
        logger.info("Tenant '%s' already exists — skipping provision.", slug)
        return record

    record = TenantConfigRecord(
        tenant_slug=slug,
        tenant_name=name,
        config_json=json.dumps(initial_config or {}),
        is_active=True,
    )
    db.add(record)
    await db.flush()
    logger.info("Provisioned new tenant: %s (%s)", slug, name)
    return record
