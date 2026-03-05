"""
Tenant isolation helpers for database queries.

Strategy: shared schema with tenant_slug column on every table.
All queries must be scoped to a tenant_slug — never query cross-tenant.

For stricter isolation (e.g. regulated industries), switch to
schema-per-tenant by overriding the SQLAlchemy connection per request.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.models.messages import MessageRecord
from src.utils.ids import new_event_id


class TenantRepository:
    """
    Scoped data access for a single tenant.

    Instantiate once per request:
        repo = TenantRepository(db, tenant_slug="acme")
    """

    def __init__(self, db: AsyncSession, tenant_slug: str) -> None:
        self._db = db
        self._slug = tenant_slug

    async def get_session_history(
        self, session_id: str, limit: int = 20
    ) -> list[MessageRecord]:
        """Return the last `limit` turns for a session, oldest-first."""
        result = await self._db.execute(
            select(MessageRecord)
            .where(
                MessageRecord.tenant_slug == self._slug,
                MessageRecord.session_id == session_id,
            )
            .order_by(MessageRecord.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def save_turn(
        self,
        session_id: str,
        user_id: str,
        channel: str,
        role: str,
        content: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> MessageRecord:
        record = MessageRecord(
            tenant_slug=self._slug,
            session_id=session_id,
            user_id=user_id,
            channel=channel,
            role=role,
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        self._db.add(record)
        await self._db.flush()
        return record
