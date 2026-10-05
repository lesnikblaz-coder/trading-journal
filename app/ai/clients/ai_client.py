from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.ai import AITradeReviewInput, AITradeReviewResponse, AIAnalysisResponse


class AIClient(ABC):
    @abstractmethod
    async def generate_trade_review(self, data: AITradeReviewInput, trade_id: UUID, user_id: UUID) -> AITradeReviewResponse:
        pass

    async def analyze_trading_system(self, question: str, system_id: UUID, user_id: UUID) -> AIAnalysisResponse:
        pass