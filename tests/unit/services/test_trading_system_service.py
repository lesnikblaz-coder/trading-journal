import pytest

from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, timezone

from app import enums
from app.database.models.trading_system import TradingSystem
from app.repositories.trading_system import TradingSystemRepo
from app.services.trading_system import TradingSystemService
from app.schemas import trading_system as sc


@pytest.fixture
def _trading_system_repo():
    return AsyncMock(spec=TradingSystemRepo)

@pytest.fixture
def _service(_trading_system_repo):
    return TradingSystemService(trading_system_repo=_trading_system_repo)

@pytest.fixture
def _user_id():
    return uuid4()

@pytest.fixture
def _trading_system(_user_id):
    return TradingSystem(
        id=uuid4(),
        user_id=_user_id,
        name="Test",
        asset_class=enums.AssetClass.ALL,
        timeframe=enums.TradeTimeframe.ONE_HOUR,
        setup_requirements="Strong momentum",
        entry_rules="Enter after price pulls back under 10 and 20 EMA, breaks back above and creates a valid buy-stop.",
        created_at=datetime.now(timezone.utc),
        is_active=True,
    )

@pytest.fixture
def _trading_system_request():
    return sc.TradingSystemRequest(
        name="Test",
        asset_class=enums.AssetClass.ALL,
        timeframe=enums.TradeTimeframe.ONE_HOUR,
        setup_requirements="Strong momentum",
        entry_rules="Enter after price pulls back under 10 and 20 EMA, breaks back above and creates a valid buy-stop."
    )

async def test_create_success(
        _service,
        _user_id,
        _trading_system_repo,
        _trading_system,
        _trading_system_request
):
    _trading_system_repo.create.return_value = _trading_system

    result = await _service.create(
        request=_trading_system_request,
        user_id=_user_id
    )

    assert result is _trading_system

    _trading_system_repo.create.assert_awaited_once()

    created = _trading_system_repo.create.call_args.args[0]

    assert created.user_id == _user_id
    assert created.name == _trading_system_request.name
    assert created.description == _trading_system_request.description
    assert created.asset_class == _trading_system_request.asset_class
    assert created.timeframe == _trading_system_request.timeframe

async def test_get_by_user(
        _trading_system_repo,
        _trading_system,
        _service,
        _user_id
):
    _trading_system_repo.get_by_user.return_value = [_trading_system]

    result = await _service.get_by_user(_user_id)

    assert len(result) == 1
    assert isinstance(result[0], sc.TradingSystemResponse)

    assert result[0].id == _trading_system.id
    assert result[0].user_id == _user_id
    assert result[0].name == _trading_system.name

    _trading_system_repo.get_by_user.assert_awaited_once_with(_user_id)

async def test_get_by_id(
        _service,
        _trading_system,
        _trading_system_repo,
        _user_id
):
    _trading_system_repo.get_by_id.return_value = _trading_system

    result = await _service.get_by_id(
        trading_system_id=_trading_system.id,
        user_id=_user_id
    )

    assert result is _trading_system

    _trading_system_repo.get_by_id.assert_awaited_once_with(
        entity_id=_trading_system.id,
        user_id=_user_id
    )

async def test_update(
        _service,
        _trading_system,
        _trading_system_repo,
        _user_id
):
    update_data = sc.TradingSystemUpdate(
        name="test update name"
    )

    _trading_system.name = "test update name"
    _trading_system_repo.update.return_value = _trading_system

    result = await _service.update(
        trading_system_id=_trading_system.id,
        user_id=_user_id,
        update_data=update_data
    )

    assert result is _trading_system

    _trading_system_repo.update.assert_awaited_once_with(
        entity_id=_trading_system.id,
        user_id=_user_id,
        update_data={
            "name": "test update name"
        }
    )

async def test_delete_by_id(
    _service,
    _trading_system_repo,
    _trading_system,
    _user_id,
):
    await _service.delete_by_id(
        trading_system_id=_trading_system.id,
        user_id=_user_id,
    )

    _trading_system_repo.delete.assert_awaited_once_with(
        entity_id=_trading_system.id,
        user_id=_user_id,
    )