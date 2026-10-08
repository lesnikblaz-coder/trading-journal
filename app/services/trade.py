from uuid import UUID
from decimal import Decimal

from app.repositories.trade import TradeRepo
from app.repositories.trading_system import TradingSystemRepo
from app.schemas import trade as sc
from app.exceptions.custom import InvalidTradingSystemError, InvalidTradeDataValuesError, EntityNotFoundError
from app.database.models.trade import Trade
from app.enums import TradeDirection, TradeStatus
from app.services.trade_calculations import TradeCalculations


class TradeService:
    def __init__(self, trade_repo: TradeRepo, trading_system_repo: TradingSystemRepo):
        self.trade_repo = trade_repo
        self.trading_system_repo = trading_system_repo

    async def create(self, system_id: UUID, request: sc.TradeCreateRequest, user_id: UUID) -> Trade:

        # checks whether trading system exists and belongs to the current user
        if not await self.trading_system_repo.get_by_id(system_id, user_id):
            raise InvalidTradingSystemError()


        if (
                (request.direction is TradeDirection.BULLISH and request.entry_price <= request.stop_loss_price)
                or
                (request.direction is TradeDirection.BEARISH and request.entry_price >= request.stop_loss_price)
        ):
            raise InvalidTradeDataValuesError()

        calculated_data = {}
        status = TradeStatus.ACTIVE
        quantity = int(self._calculate_quantity(request))

        # exit price must not be None/0 etc. to calculate trade results
        if request.exit_price:
            calculated_data = self._calculate_trade_results(request)
            status = TradeStatus.CLOSED


        trade = Trade(
            user_id=user_id,
            trading_system_id=system_id,
            status=status,
            quantity=round(quantity, 2),
            **request.model_dump(exclude_none=True),
            **calculated_data
        )

        return await self.trade_repo.create(trade)

    async def get_all_for_system(self, system_id: UUID, user_id: UUID) -> list[sc.TradeResponse]:
        result = await self.trade_repo.get_all_for_system(system_id, user_id)

        return [sc.TradeResponse.model_validate(r) for r in result]

    async def get_by_id(self, trade_id: UUID, user_id: UUID) -> Trade | None:
        trade = await self.trade_repo.get_by_id(trade_id, user_id)

        if not trade:
            raise EntityNotFoundError(detail="No trade found.")

        return trade

    async def update(self, trade_id: UUID, user_id: UUID, request: sc.TradeUpdateRequest) -> Trade:
        trade = await self.trade_repo.get_by_id(trade_id, user_id)

        if trade is None:
            raise EntityNotFoundError("Trade not found.")

        update_data = request.model_dump(exclude_unset=True)

        if update_data.get("exit_price") is not None:

            existing_data = {
                field: getattr(trade, field)
                for field in sc.TradeCalculationInput.model_fields
            }

            merged_data = {
                **existing_data,
                **update_data
            }

            calculation_input = sc.TradeCalculationInput.model_validate(merged_data)

            calculated_data = self._calculate_trade_results(calculation_input)

            update_data.update(calculated_data)
            update_data["status"] = TradeStatus.CLOSED


        return await self.trade_repo.update_fetched_trade(
            trade=trade,
            update_data=update_data
        )

    async def delete(self, trade_id: UUID, user_id: UUID) -> None:
        await self.trade_repo.delete(
            entity_id=trade_id,
            user_id=user_id
        )

    @staticmethod
    def _calculate_trade_results(trade: sc.TradeCalculationInput) -> dict[str, Decimal]:
        trade_calc = TradeCalculations(trade)

        return {
            "realized_pnl": trade_calc.calculate_pnl(),
            "realized_pnl_percent": trade_calc.calculate_pnl_percent(),
            "result_r": trade_calc.calculate_r_multiple()
        }

    @staticmethod
    def _calculate_quantity(data: sc.TradeCreateRequest) -> Decimal:
        return data.dollar_risk / abs(data.entry_price - data.stop_loss_price)