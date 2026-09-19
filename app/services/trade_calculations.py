from decimal import Decimal

from app.enums import TradeDirection
from app.schemas.trade import TradeCreateRequest
from app.database.models.trade import Trade


class TradeCalculations:
    def __init__(self, trade: Trade | TradeCreateRequest):
        self.trade = trade

    def calculate_pnl(self) -> Decimal:
        r_multiple = self.calculate_r_multiple()

        return r_multiple * self.trade.dollar_risk


    def calculate_pnl_percent(self) -> Decimal:
        pnl = self.calculate_pnl()

        acc_size = (100 / self.trade.percent_risk) * self.trade.dollar_risk

        return (pnl / acc_size) * 100

    def calculate_r_multiple(self) -> Decimal:
        if self.trade.direction is TradeDirection.BULLISH:
            return (self.trade.exit_price - self.trade.entry_price) / (self.trade.entry_price - self.trade.stop_loss_price)

        # if not bullish, it's bearish
        return (self.trade.entry_price - self.trade.exit_price) / (self.trade.stop_loss_price - self.trade.entry_price)