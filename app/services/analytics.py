from app.repositories.trade import TradeRepo
from app.schemas import analytics as sc
from app.services.overview_calculations import OverviewCalculations


class AnalyticsService:
    def __init__(self, trade_repo: TradeRepo):
        self.repo = trade_repo

    async def overview(self, trading_system_id, user_id) -> sc.AnalyticsOverviewResponse:
        trades = await self.repo.get_all_for_system(trading_system_id, user_id)

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