import pytest
from uuid import uuid4
from decimal import Decimal

from app.services.trade_calculations import TradeCalculations
from app.database.models.trade import Trade
from app import enums


_reusable_data = {
    "user_id": uuid4(),
    "trading_system_id": uuid4(),
    "symbol": "TEST",
    "percent_risk": Decimal("1"),
    "dollar_risk": Decimal("1000"),
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

async def test_bearish_winning_trade_r_multiple():
    trade = Trade(
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("105"),
        exit_price=Decimal("90"),
        status=enums.TradeStatus.CLOSED,
        direction=enums.TradeDirection.BEARISH,
        **_reusable_data
    )

    calculations = TradeCalculations(trade=trade)

    result = calculations.calculate_r_multiple()

    assert result == Decimal("2")

async def test_bearish_losing_trade_r_multiple():
    trade = Trade(
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("105"),
        exit_price=Decimal("105"),
        status=enums.TradeStatus.CLOSED,
        direction=enums.TradeDirection.BEARISH,
        **_reusable_data
    )

    calculations = TradeCalculations(trade=trade)

    result = calculations.calculate_r_multiple()

    assert result == Decimal("-1")

async def test_breakeven_trade_r_multiple():
    trade = Trade(
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("95"),
        exit_price=Decimal("100"),
        status=enums.TradeStatus.CLOSED,
        direction=enums.TradeDirection.BULLISH,
        **_reusable_data
    )

    calculations = TradeCalculations(trade=trade)

    result = calculations.calculate_r_multiple()

    assert result == Decimal("0")

async def test_trade_without_exit_has_no_r_multiple():
    trade = Trade(
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("95"),
        status=enums.TradeStatus.ACTIVE,
        direction=enums.TradeDirection.BULLISH,
        **_reusable_data
    )

    calculations = TradeCalculations(trade=trade)

    with pytest.raises(TypeError):
        calculations.calculate_r_multiple()

async def test_pnl():
    trade = Trade(
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("95"),
        exit_price=Decimal("110"),
        status=enums.TradeStatus.CLOSED,
        direction=enums.TradeDirection.BULLISH,
        **_reusable_data
    )

    calculations = TradeCalculations(trade=trade)

    assert calculations.calculate_pnl() == Decimal("2000")

async def test_pnl_percent():
    trade = Trade(
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("95"),
        exit_price=Decimal("110"),
        status=enums.TradeStatus.CLOSED,
        direction=enums.TradeDirection.BULLISH,
        **_reusable_data
    )

    calculations = TradeCalculations(trade=trade)

    assert calculations.calculate_pnl_percent() == Decimal("2")

async def test_pnl_without_exit_raises():
    trade = Trade(
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("95"),
        status=enums.TradeStatus.ACTIVE,
        direction=enums.TradeDirection.BULLISH,
        **_reusable_data
    )

    calculations = TradeCalculations(trade=trade)

    with pytest.raises(TypeError):
        calculations.calculate_pnl()
        calculations.calculate_pnl_percent()