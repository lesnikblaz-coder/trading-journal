from decimal import Decimal
from dataclasses import dataclass
from typing import Sequence

from app.database.models.trade import Trade
from app.services.trade_calculations import TradeCalculations


@dataclass
class OverviewCalculationsResult:
    total_trades: int
    winners: int
    losers: int
    breakevens: int
    win_rate: float
    avg_winner: float
    avg_loser: float
    profit_factor: float | None
    expectancy: float


class OverviewCalculations:
    def __init__(self, trades: Sequence[Trade]):
        self.trades = trades

    def calculate(self) -> OverviewCalculationsResult:
        total_trades = len(self.trades)

        winners = 0
        losers = 0
        breakevens = 0

        winner_r_multiples: list[Decimal] = []
        loser_r_multiples: list[Decimal] = []
        all_r_multiples: list[Decimal] = []

        gross_profit = Decimal("0")
        gross_loss = Decimal("0")

        for trade in self.trades:
            trade_calc = TradeCalculations(
                trade.entry_price,
                trade.stop_loss_price,
                trade.exit_price,
                trade.direction,
            )

            pnl = trade_calc.calculate_pnl(trade.dollar_risk)
            r_multiple = trade_calc.calculate_r_multiple()

            all_r_multiples.append(r_multiple)

            if pnl > 0:
                winners += 1
                winner_r_multiples.append(r_multiple)
                gross_profit += pnl

            elif pnl < 0:
                losers += 1
                loser_r_multiples.append(r_multiple)
                gross_loss += abs(pnl)

            else:
                breakevens += 1

        return OverviewCalculationsResult(
            total_trades=total_trades,
            winners=winners,
            losers=losers,
            breakevens=breakevens,
            win_rate=self._calculate_win_rate(total_trades, winners),
            avg_winner=self._calculate_average(winner_r_multiples),
            avg_loser=self._calculate_average(loser_r_multiples),
            profit_factor=self._calculate_profit_factor(gross_profit, gross_loss),
            expectancy=self._calculate_average(all_r_multiples)
        )

    @staticmethod
    def _calculate_win_rate(total_trades: int, winners: int) -> float:
        if total_trades == 0:
            return 0.0

        return (winners / total_trades) * 100

    @staticmethod
    def _calculate_average(values: Sequence[Decimal]) -> float:
        if not values:
            return 0.0

        return float(sum(values) / len(values))

    @staticmethod
    def _calculate_profit_factor(gross_profit: Decimal, gross_loss: Decimal) -> float | None:
        if gross_loss == 0:
            return None

        return float(gross_profit / gross_loss)