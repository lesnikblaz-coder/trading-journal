from uuid import UUID

from app.ai.ai_client import AIClient
from app.repositories.trade import TradeRepo
from app.exceptions.custom import EntityNotFoundError
from app.schemas import ai as sc


class TradeReviewService:
    def __init__(self, client: AIClient, trade_repo: TradeRepo):
        self.client = client
        self.trade_repo = trade_repo

    async def generate_trade_review(self, trade_id: UUID, user_id: UUID) -> sc.AITradeReviewResponse:
        trade = await self.trade_repo.get_by_id_fetch_system(trade_id, user_id) # eager loads trading_system

        if not trade:
            raise EntityNotFoundError(detail="Trade not found. Unable to generate trade review.")

        trade_input = sc.TradeInput.model_validate(trade)
        trade_system_input = sc.TradingSystemInput.model_validate(trade.trading_system)

        data = sc.AITradeReviewInput.model_validate({
            "trade": trade_input,
            "trading_system": trade_system_input,
        })

        return await self.client.generate_trade_review(
            data=data
        )