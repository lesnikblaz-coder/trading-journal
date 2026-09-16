from google import genai

from app.ai.ai_client import AIClient
from app.core.config import settings
from app.ai.system_instructions import TRADE_REVIEW_INSTRUCTIONS
from app.ai.prompts.trade_review import build_trade_review_prompt
from app.schemas.ai import AITradeReviewResponse, AITradeReviewInput


class GeminiClient(AIClient):
    def __init__(self, client: genai.client.AsyncClient): 
        self.client = client

    async def generate_trade_review(self, data: AITradeReviewInput) -> AITradeReviewResponse:
        interaction = await self.client.interactions.create(
            model=settings.GEMINI_MODEL,

            system_instruction=TRADE_REVIEW_INSTRUCTIONS,

            input=build_trade_review_prompt(
                data
            ),

            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": AITradeReviewResponse.model_json_schema()
            },
        )

        return AITradeReviewResponse.model_validate_json(
            interaction.output_text
        )