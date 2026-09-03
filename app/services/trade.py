from uuid import UUID

from app.repositories.trade import TradeRepo
from app.repositories.trading_system import TradingSystemRepo
from app.schemas import trade as sc
from app.exceptions.custom import InvalidTradingSystemError, InvalidTradeDataValuesError
from app.database.models.trade import Trade
from app.enums import TradeDirection


class TradeService:
    def __init__(self, trade_repo: TradeRepo, trading_system_repo: TradingSystemRepo):
        self.trade_repo = trade_repo
        self.trading_system_repo = trading_system_repo

    async def create(self, system_id: UUID, request: sc.TradeCreateRequest, user_id: UUID):

        # checks whether trading system exists and belongs to the current user
        if not await self.trading_system_repo.get_by_id(system_id, user_id):
            raise InvalidTradingSystemError()


        if (
                (request.direction is TradeDirection.BULLISH and request.entry_price <= request.stop_loss_price)
                or
                (request.direction is TradeDirection.BEARISH and request.entry_price >= request.stop_loss_price)
        ):
            return InvalidTradeDataValuesError


        if request.exit_price is not None:
            if (
                    (request.direction is TradeDirection.BULLISH and request.exit_price <= request.entry_price)
                    or
                    (request.direction is TradeDirection.BEARISH and request.entry_price <= request.exit_price)
            ):
                return InvalidTradeDataValuesError()


        trade = Trade(
            user_id=user_id,
            trading_system_id=system_id,
            **request.model_dump(exclude_none=True)
        )

        return await self.trade_repo.create(trade)