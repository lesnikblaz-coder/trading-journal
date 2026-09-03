from uuid import UUID
from typing import Sequence
from sqlalchemy import select

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