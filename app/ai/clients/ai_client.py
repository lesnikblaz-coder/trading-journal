from abc import ABC, abstractmethod

from app.schemas.ai import AITradeReviewInput, AITradeReviewResponse


class AIClient(ABC):
    @abstractmethod
    async def generate_trade_review(self, data: AITradeReviewInput) -> AITradeReviewResponse:
        pass