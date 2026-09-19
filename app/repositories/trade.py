from uuid import UUID
from typing import Sequence
from sqlalchemy import select, func, case, RowMapping
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from app.repositories.base import BaseRepo
from app.database.models.trade import Trade
from app.enums import TradeDirection


class TradeRepo(BaseRepo[Trade]):
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

    async def get_for_month(self, year: int, month: int, system_id: UUID, user_id: UUID) -> Sequence[Trade]:
        start = datetime(year, month, 1, tzinfo=timezone.utc)

        if month == 12:
            end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(year, month + 1, 1, tzinfo=timezone.utc)

        result = await self.session.execute(
            select(Trade)
            .where(
                Trade.user_id == user_id,
                Trade.trading_system_id == system_id,
                Trade.created_at >= start,
                Trade.created_at < end
            )
        )

        return result.scalars().all()

    async def get_by_id_fetch_system(self, trade_id: UUID, user_id: UUID | None = None) -> Trade | None:
        query = (
            select(Trade)
            .where(Trade.id == trade_id)
            .options(selectinload(Trade.trading_system))
        )

        if user_id is not None:
            query = query.where(Trade.user_id == user_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def get_grouped_by_symbol(self, system_id: UUID, user_id: UUID) -> Sequence[RowMapping]:
        query = select(
            Trade.symbol,
            func.sum(Trade.realized_pnl).label("total_profit"),
            func.sum(Trade.result_r).label("r_result"),
            func.avg(Trade.entry_price).label("average_price"),
            func.sum(case(
                (Trade.direction == TradeDirection.BULLISH, Trade.quantity),
                (Trade.direction == TradeDirection.BEARISH, -Trade.quantity),
                else_=0,)
            ).label("net_quantity"),
        ).where(
            Trade.trading_system_id == system_id,
            Trade.user_id == user_id,
        ).group_by(Trade.symbol)

        result = await self.session.execute(query)

        return result.mappings().all()