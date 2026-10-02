import pytest

from uuid import uuid4
from decimal import Decimal

from app import enums
from app.database.models.trade import Trade
from app.services.overview_calculations import OverviewCalculations

def make_trade(
        *,
        entry: str,
        stop: str,
        exit: str | None,
        direction: enums.TradeDirection = enums.TradeDirection.BULLISH,
        dollar_risk: str = "1000",
        status: enums.TradeStatus | None = None
) -> Trade:
    if status is None:
        status = (
            enums.TradeStatus.CLOSED
            if exit is not None
            else enums.TradeStatus.ACTIVE
        )

    return Trade(
        user_id=uuid4(),
        trading_system_id=uuid4(),
        symbol="TEST",
        direction=direction,
        entry_price=Decimal(entry),
        stop_loss_price=Decimal(stop),
        exit_price=Decimal(exit) if exit is not None else None,
        dollar_risk=Decimal(dollar_risk),
        percent_risk=Decimal("1"),
        status=status,
    )

# ==========================
# TESTS
# ==========================
def test_empty_trades():
    result = OverviewCalculations([]).calculate()

    assert result.total_trades == 0
    assert result.winners == 0
    assert result.losers == 0
    assert result.breakevens == 0
    assert result.win_rate == 0
    assert result.avg_winner == 0
    assert result.avg_loser == 0
    assert result.profit_factor == 0
    assert result.expectancy == 0

def test_calculate_mixed_trades():
    trades = [
        make_trade(
            entry="100",
            stop="95",
            exit="110",
        ), # +2R

        make_trade(
            entry="100",
            stop="95",
            exit="115",
        ), # +3R

        make_trade(
            entry="100",
            stop="95",
            exit="95",
        ), # -1R

        make_trade(
            entry="100",
            stop="95",
            exit="90",
        ), # -2R

        make_trade(
            entry="100",
            stop="95",
            exit="100",
        ), # 0R
    ]

    result = OverviewCalculations(trades).calculate()

    assert result.total_trades == 5
    assert result.winners == 2
    assert result.losers == 2
    assert result.breakevens == 1

    assert result.win_rate == 40.0

    assert result.avg_winner == pytest.approx(2.5)
    assert result.avg_loser == pytest.approx(-1.5)

    assert result.profit_factor == pytest.approx(5/3)
    assert result.expectancy == pytest.approx(0.40)

def test_all_winners():
    trades = [
        make_trade(
            entry="100",
            stop="95",
            exit="110",
        ),  # +2R

        make_trade(
            entry="100",
            stop="95",
            exit="115",
        ),  # +3R
    ]

    result = OverviewCalculations(trades).calculate()

    assert result.total_trades == 2
    assert result.winners == 2
    assert result.losers == 0
    assert result.breakevens == 0

    assert result.win_rate == 100
    assert result.avg_winner == pytest.approx(2.5)
    assert result.avg_loser == 0
    assert result.profit_factor == 0
    assert result.expectancy == pytest.approx(2.5)

def test_all_losers():
    trades = [
        make_trade(
            entry="100",
            stop="95",
            exit="95",
        ),  # -1R

        make_trade(
            entry="100",
            stop="95",
            exit="90",
        ),  # -2R
    ]

    result = OverviewCalculations(trades).calculate()

    assert result.total_trades == 2
    assert result.winners == 0
    assert result.losers == 2
    assert result.breakevens == 0

    assert result.win_rate == 0
    assert result.avg_winner == 0
    assert result.avg_loser == pytest.approx(-1.5)
    assert result.profit_factor == 0
    assert result.expectancy == pytest.approx(-1.5)

def test_all_breakevens():
    trades = [
        make_trade(
            entry="100",
            stop="95",
            exit="100",
        ),

        make_trade(
            entry="100",
            stop="95",
            exit="100",
        ),

        make_trade(
            entry="100",
            stop="95",
            exit="100",
        ),
    ]

    result = OverviewCalculations(trades).calculate()

    assert result.total_trades == 3
    assert result.winners == 0
    assert result.losers == 0
    assert result.breakevens == 3

    assert result.win_rate == 0
    assert result.avg_winner == 0
    assert result.avg_loser == 0
    assert result.profit_factor == 0
    assert result.expectancy == 0

def test_active_trade_is_excluded_from_results_but_included_in_total():
    trades = [
        make_trade(
            entry="100",
            stop="95",
            exit="110",
        ),  # +2R

        make_trade(
            entry="100",
            stop="95",
            exit="95",
        ),  # -1R

        make_trade(
            entry="100",
            stop="95",
            exit="100",
        ),  # 0R

        make_trade(
            entry="100",
            stop="95",
            exit=None,
        ),  # active
    ]

    result = OverviewCalculations(trades).calculate()

    assert result.total_trades == 4

    assert result.winners == 1
    assert result.losers == 1
    assert result.breakevens == 1

    assert result.win_rate == 25

    assert result.avg_winner == pytest.approx(2)
    assert result.avg_loser == pytest.approx(-1)

    assert result.profit_factor == pytest.approx(2)
    assert result.expectancy == pytest.approx(1 / 3)