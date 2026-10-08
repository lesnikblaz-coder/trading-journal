import pytest

from unittest.mock import AsyncMock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone

from app import enums
from app.database.models.trade import Trade
from app.repositories.trade import TradeRepo
from app.repositories.trading_system import TradingSystemRepo
from app.services.trade import TradeService
from app.schemas import trade as sc
from app.exceptions import custom as err


@pytest.fixture
def _trade_repo():
    return AsyncMock(spec=TradeRepo)

@pytest.fixture
def _trading_system_repo():
    return AsyncMock(spec=TradingSystemRepo)

@pytest.fixture
def _service(_trade_repo, _trading_system_repo):
    return TradeService(
        trade_repo=_trade_repo,
        trading_system_repo=_trading_system_repo
    )

@pytest.fixture
def _user_id():
    return uuid4()

@pytest.fixture
def _system_id():
    return uuid4()

@pytest.fixture
def _trade_create_request():
    return sc.TradeCreateRequest(
        symbol="TEST",
        direction=enums.TradeDirection.BULLISH,
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("95"),
        dollar_risk=Decimal("1000"),
        percent_risk=Decimal("1")
    )

@pytest.fixture
def _trade(_user_id, _system_id):
    return Trade(
        id=uuid4(),
        user_id=_user_id,
        trading_system_id=_system_id,
        symbol="TEST",
        direction=enums.TradeDirection.BULLISH,
        entry_price=Decimal("100"),
        stop_loss_price=Decimal("95"),
        dollar_risk=Decimal("1000"),
        percent_risk=Decimal("1"),
        status=enums.TradeStatus.ACTIVE,
        created_at=datetime.now(timezone.utc)
    )


async def test_create(
        _user_id,
        _system_id,
        _trade_create_request,
        _trade_repo,
        _trading_system_repo,
        _service,
        _trade
):
    _trading_system_repo.get_by_id.return_value = True
    _trade_repo.create.return_value = _trade

    result = await _service.create(
        user_id=_user_id,
        system_id=_system_id,
        request=_trade_create_request,
    )

    assert result is _trade

    _trade_repo.create.assert_awaited_once()

    created = _trade_repo.create.call_args.args[0]

    assert created.user_id == _user_id
    assert created.trading_system_id == _system_id
    assert created.symbol == _trade.symbol
    assert created.entry_price == _trade.entry_price
    assert created.exit_price == _trade.exit_price
    assert created.stop_loss_price == _trade.stop_loss_price
    assert created.direction == _trade.direction
    assert created.dollar_risk == _trade.dollar_risk
    assert created.percent_risk == _trade.percent_risk
    assert created.realized_pnl is None
    assert created.realized_pnl_percent is None
    assert created.result_r is None


async def test_create_with_invalid_trading_system(
        _user_id,
        _system_id,
        _trade_create_request,
        _trade_repo,
        _trading_system_repo,
        _service
):
    _trading_system_repo.get_by_id.return_value = None

    with pytest.raises(err.InvalidTradingSystemError):
        await _service.create(
            user_id=_user_id,
            system_id=_system_id,
            request=_trade_create_request,
        )

    _trade_repo.create.assert_not_awaited()


async def test_get_all_for_system(
        _service,
        _user_id,
        _system_id,
        _trade_repo,
        _trade,
):
    _trade_repo.get_all_for_system.return_value = [_trade]

    result = await _service.get_all_for_system(
        system_id=_system_id,
        user_id=_user_id
    )

    assert len(result) == 1
    assert isinstance(result[0], sc.TradeResponse)

    assert result[0].id == _trade.id
    assert result[0].user_id == _user_id
    assert result[0].trading_system_id == _system_id
    assert result[0].symbol == _trade.symbol

    _trade_repo.get_all_for_system.assert_awaited_once_with(
        _system_id,
        _user_id
    )


async def test_get_by_id(
        _service,
        _user_id,
        _trade,
        _trade_repo
):
    _trade_repo.get_by_id.return_value = _trade

    result = await _service.get_by_id(
        trade_id=_trade.id,
        user_id=_user_id
    )

    assert result is _trade

    _trade_repo.get_by_id.assert_awaited_once_with(
        _trade.id,
        _user_id
    )


async def test_update(
        _service,
        _user_id,
        _trade,
        _trade_repo,
):
    update_data = sc.TradeUpdateRequest(
        symbol="TEST_UPDT"
    )
    _trade.symbol = "TEST_UPDT"
    _trade_repo.get_by_id.return_value = _trade
    _trade_repo.update_fetched_trade.return_value = _trade

    result = await _service.update(
        trade_id=_trade.id,
        user_id=_user_id,
        request=update_data
    )

    assert result is _trade

    _trade_repo.update_fetched_trade.assert_awaited_once_with(
        trade=_trade,
        update_data={
            "symbol": "TEST_UPDT"
        }
    )


async def test_delete_by_id(
        _service,
        _user_id,
        _trade,
        _trade_repo
):
    await _service.delete(
        trade_id=_trade.id,
        user_id=_user_id
    )

    _trade_repo.delete.assert_awaited_once_with(
        entity_id=_trade.id,
        user_id=_user_id
    )


@pytest.mark.parametrize(
    ("direction", "entry", "stop"),
    [
        (enums.TradeDirection.BULLISH, Decimal("100"), Decimal("100")),
        (enums.TradeDirection.BULLISH, Decimal("100"), Decimal("105")),
        (enums.TradeDirection.BEARISH, Decimal("100"), Decimal("100")),
        (enums.TradeDirection.BEARISH, Decimal("100"), Decimal("95")),
    ]
)
async def test_create_with_invalid_stop(
        direction,
        entry,
        stop,
        _user_id,
        _system_id,
        _trade_create_request,
        _trade_repo,
        _trading_system_repo,
        _service,
):
    _trade_create_request.direction = direction
    _trade_create_request.entry_price = entry
    _trade_create_request.stop_loss_price = stop

    _trading_system_repo.get_by_id.return_value = True

    with pytest.raises(err.InvalidTradeDataValuesError):
        await _service.create(
            user_id=_user_id,
            system_id=_system_id,
            request=_trade_create_request
        )

    _trade_repo.create.assert_not_awaited()


async def test_create_closed_calculations(
        _service,
        _user_id,
        _system_id,
        _trade_create_request,
        _trade_repo,
        _trading_system_repo,
        _trade
):
    _trading_system_repo.get_by_id_return_value = True
    _trade_create_request.exit_price = Decimal("110")

    result = await _service.create(
        user_id=_user_id,
        system_id=_system_id,
        request=_trade_create_request
    )

    _trade_repo.create.assert_awaited_once()

    assert result is not None

    created = _trade_repo.create.call_args.args[0]

    assert created.exit_price == _trade_create_request.exit_price

    assert created.realized_pnl is not None
    assert created.realized_pnl_percent is not None
    assert created.result_r is not None
    assert created.status == enums.TradeStatus.CLOSED


async def test_get_by_id_trade_none_raises(
        _service,
        _user_id,
        _trade,
        _trade_repo
):
    _trade_repo.get_by_id.return_value = None

    with pytest.raises(err.EntityNotFoundError):
        await _service.get_by_id(
            trade_id=_trade.id,
            user_id=_user_id
        )