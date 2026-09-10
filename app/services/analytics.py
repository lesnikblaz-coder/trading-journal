from uuid import UUID

from app.repositories.trade import TradeRepo
from app.schemas import analytics as sc
from app.services.overview_calculations import OverviewCalculations
from app.database.models.trade import Trade


class AnalyticsService:
    def __init__(self, trade_repo: TradeRepo):
        self.repo = trade_repo

    @staticmethod
    async def _overview_base(trades: list[Trade]) -> sc.AnalyticsOverviewResponse:
        if not trades:
            return sc.AnalyticsOverviewResponse(
                total_trades=0, winning_trades=0, losing_trades=0,
                breakevens=0, win_rate=0, avg_winner=0,
                avg_loser=0, profit_factor=0, expectancy=0
            )

        result = OverviewCalculations(trades).calculate()

        return sc.AnalyticsOverviewResponse(
            total_trades=result.total_trades,
            winning_trades=result.winners,
            losing_trades=result.losers,
            breakevens=result.breakevens,
            win_rate=result.win_rate,
            avg_winner=result.avg_winner,
            avg_loser=result.avg_loser,
            profit_factor=result.profit_factor,
            expectancy=result.expectancy
        )

    async def overview_by_system_id(self, trading_system_id: UUID, user_id: UUID) -> sc.AnalyticsOverviewResponse:
        trades = list(await self.repo.get_all_for_system(trading_system_id, user_id))

        return await self._overview_base(trades)

    async def overview_monthly_performance(self, year: int, month: int, user_id: UUID) -> sc.AnalyticsOverviewResponse:
        trades = list(await self.repo.get_for_month(year, month, user_id))

        return await self._overview_base(trades)