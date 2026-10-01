from uuid import uuid4
from decimal import Decimal

from app.services.trade_calculations import TradeCalculations
from app.database.models.trade import Trade
from app import enums


_reusable_data = {
    "user_id": uuid4(),
    "trading_system_id": uuid4(),
    "symbol": "TEST",
}


async def test_bullish_winning_trade_r_multiple():
    trade = Trade(
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("95"),
        exit_price=Decimal("110"),
        status=enums.TradeStatus.CLOSED,
        direction=enums.TradeDirection.BULLISH,
        **_reusable_data
    )

    calculations = TradeCalculations(trade=trade)

    result = calculations.calculate_r_multiple()

    assert result == Decimal("2")

async def test_bullish_losing_trade_r_multiple():
    trade = Trade(
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("95"),
        exit_price=Decimal("95"),
        status=enums.TradeStatus.CLOSED,
        direction=enums.TradeDirection.BULLISH,
        **_reusable_data
    )

    calculations = TradeCalculations(trade=trade)

    result = calculations.calculate_r_multiple()

    assert result == Decimal("-1")