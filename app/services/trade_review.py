from app.ai.ai_client import AIClient #?


class TradeReviewService:
    def __init__(self, client: AIClient):
        self.client = client

    async def generate_trade_review(self):
        return await self.client.generate_trade_review()