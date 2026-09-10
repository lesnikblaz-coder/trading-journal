from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from datetime import datetime, timezone

from app.repositories.base import BaseRepo
from app.database.models.trade import Trade


class TradeRepo(BaseRepo):
    model = Trade

    async def get_all_for_system(self, system_id: UUID, user_id: UUID) -> Sequence[Trade]:
        result = await self.session.execute(
            select(Trade)
            .where(
                Trade.trading_system_id == system_id,
                Trade.user_id == user_id
            )
        )

        return result.scalars().all()

    async def get_for_month(self, year: int, month: int, user_id: UUID) -> Sequence[Trade]:
        start = datetime(year, month, 1, tzinfo=timezone.utc)

        if month == 12:
            end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(year, month + 1, 1, tzinfo=timezone.utc)

        result = await self.session.execute(
            select(Trade)
            .where(
                Trade.user_id == user_id,
                Trade.created_at >= start,
                Trade.created_at < end
            )
        )

        return result.scalars().all()