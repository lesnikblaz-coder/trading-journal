from decimal import Decimal

from app.enums import TradeDirection


class TradeCalculations:
    def __init__(
            self,
            entry_price: Decimal, stop_loss_price: Decimal,
            exit_price: Decimal, direction: TradeDirection
    ):
        self.entry_price = entry_price
        self.stop_loss_price = stop_loss_price
        self.exit_price = exit_price
        self.direction = direction


    def calculate_pnl(self, dollar_risk: Decimal) -> Decimal:
        r_multiple = self.calculate_r_multiple()

        return r_multiple * dollar_risk


    def calculate_pnl_percent(self, dollar_risk: Decimal, acc_size: Decimal) -> Decimal:
        pnl = self.calculate_pnl(dollar_risk)

        return (pnl / acc_size) * 100


    def calculate_r_multiple(self) -> Decimal:
        if self.direction is TradeDirection.BULLISH:
            return (self.exit_price - self.entry_price) / (self.entry_price - self.stop_loss_price)

        # if not bullish, it's bearish
        return (self.entry_price - self.exit_price) / (self.stop_loss_price - self.entry_price)