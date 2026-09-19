import json

from google import genai
from uuid import UUID

from app.ai.clients.ai_client import AIClient
from app.core.config import settings
from app.ai.tools.system_instructions import TRADE_REVIEW_INSTRUCTIONS
from app.ai.prompts.trade_review import build_trade_review_prompt
from app.exceptions.custom import EntityNotFoundError
from app.schemas import ai as sc
from app.ai.tools.system_instructions import TRADING_ANALYST_INSTRUCTIONS
from app.ai.tools.tools import TOOLS
from app.ai.tools.analytics import AnalyticsTools
from app.repositories.trading_system import TradingSystemRepo


class GeminiClient(AIClient):
    def __init__(self, client: genai.client.AsyncClient, analytics_tools: AnalyticsTools, trading_system_repo: TradingSystemRepo):
        self.client = client
        self.analytics_tools = analytics_tools
        self.trading_system_repo = trading_system_repo


    async def generate_trade_review(self, data: sc.AITradeReviewInput) -> sc.AITradeReviewResponse:
        interaction = await self.client.interactions.create(
            model=settings.GEMINI_MODEL,

            system_instruction=TRADE_REVIEW_INSTRUCTIONS,

            input=build_trade_review_prompt(
                data
            ),

            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": sc.AITradeReviewResponse.model_json_schema()
            },
        )

        return sc.AITradeReviewResponse.model_validate_json(
            interaction.output_text
        )


    async def analyze_trading_system(self, question: str, system_id: UUID, user_id: UUID) -> sc.AIAnalysisResponse:
        system = await self.trading_system_repo.get_by_id(system_id, user_id)

        if not system:
            raise EntityNotFoundError("Trading system not found.")

        interaction = await self.client.interactions.create(
            model=settings.GEMINI_MODEL,
            system_instruction=TRADING_ANALYST_INSTRUCTIONS,
            input=question,
            tools=TOOLS
        )

        while True:

            function_calls = [
                step
                for step in interaction.steps
                if step.type == "function_call"
            ]


            if not function_calls:
                return sc.AIAnalysisResponse(
                    answer=interaction.output_text
                )

            function_results = []

            for step in function_calls:
                if step.name == "get_performance_summary":
                    result = await self.analytics_tools.get_performance_summary(
                        user_id=user_id,
                        system_id=system.id
                    )

                elif step.name == "get_performance_by_month":
                    arguments = sc.MonthSummaryArg.model_validate(step.arguments)

                    result = await self.analytics_tools.get_performance_by_month(
                        user_id=user_id,
                        system_id=system_id,
                        **arguments.model_dump()
                    )

                elif step.name == "get_performance_by_symbol":
                    result = await self.analytics_tools.get_performance_by_symbol(
                        user_id=user_id,
                        system_id=system_id,
                    )

                else:
                    raise ValueError(f"Unknown function call: {step.name}")

                function_results.append({
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [{
                        "type": "text",
                        "text": json.dumps(result, default=str)
                    }]
                })

            interaction = await self.client.interactions.create(
                model=settings.GEMINI_MODEL,
                system_instruction=TRADING_ANALYST_INSTRUCTIONS,
                tools=TOOLS,
                previous_interaction_id=interaction.id,
                input=function_results
            )