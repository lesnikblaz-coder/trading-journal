from uuid import UUID

from app.ai.clients.ai_client import AIClient
from app.repositories.trade import TradeRepo
from app.repositories.trading_system import TradingSystemRepo
from app.exceptions.custom import EntityNotFoundError
from app.schemas import ai as sc


class AIService:
    def __init__(self, client: AIClient, trade_repo: TradeRepo, trading_system_repo: TradingSystemRepo):
        self.client = client
        self.trade_repo = trade_repo
        self.trading_system_repo = trading_system_repo

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
            data=data,
            trade_id=trade_id,
            user_id=user_id,
        )

    async def analyze_trading_system(self, question: str, system_id: UUID, user_id: UUID) -> sc.AIAnalysisResponse:
        system = await self.trading_system_repo.get_by_id(system_id, user_id)

        if not system:
            raise EntityNotFoundError("Trading system not found.")

        return await self.client.analyze_trading_system(
            question=question,
            system_id=system_id,
            user_id=user_id,
        )