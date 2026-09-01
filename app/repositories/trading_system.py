from uuid import UUID
from typing import Sequence
from sqlalchemy import select

from app.repositories.base import BaseRepo
from app.database.models.trading_system import TradingSystem


class TradingSystemRepo(BaseRepo):
    async def get_by_user(self, user_id: UUID) -> Sequence[TradingSystem]:
        result = await self.session.execute(
            select(TradingSystem)
            .where(TradingSystem.user_id == user_id)
        )

        return result.scalars().all()