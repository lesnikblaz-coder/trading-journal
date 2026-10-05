import json

from google import genai
from uuid import UUID

from app.ai.clients.ai_client import AIClient
from app.core.config import settings
from app.ai.tools.system_instructions import TRADE_REVIEW_INSTRUCTIONS
from app.ai.prompts.trade_review import build_trade_review_prompt
from app.exceptions.custom import AIInteractionLimitError
from app.schemas import ai as sc
from app.ai.tools.system_instructions import TRADING_ANALYST_INSTRUCTIONS
from app.ai.tools.tools import TOOLS
from app.ai.tools.analytics import AnalyticsTools
from app.core.logging_config import logger


class GeminiClient(AIClient):
    def __init__(self, client: genai.client.AsyncClient, analytics_tools: AnalyticsTools):
        self.client = client
        self.analytics_tools = analytics_tools


    async def generate_trade_review(self, data: sc.AITradeReviewInput, trade_id: UUID, user_id: UUID) -> sc.AITradeReviewResponse:
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

        logger.info("AI trade review generation complete")

        return sc.AITradeReviewResponse.model_validate_json(
            interaction.output_text
        )


    async def analyze_trading_system(self, question: str, system_id: UUID, user_id: UUID) -> sc.AIAnalysisResponse:
        interaction = await self.client.interactions.create(
            model=settings.GEMINI_MODEL,
            system_instruction=TRADING_ANALYST_INSTRUCTIONS,
            input=question,
            tools=TOOLS
        )

        tools_used = []
        #tool_call_count = 0

        for _ in range(settings.MAX_AI_TOOL_ITERATIONS):

            function_calls = [
                step
                for step in interaction.steps
                if step.type == "function_call"
            ]

            if not function_calls:
                return sc.AIAnalysisResponse(
                    answer=interaction.output_text,
                    tools_used=tools_used
                )

            #if tool_call_count + len(function_calls) > settings.MAX_AI_TOOL_CALLS:
                #logger. --- also  function calls = function calls + len(function_calls) after each loop
                #raise AIInteractionLimitError()

            function_results = []

            for step in function_calls:
                tools_used.append(step.name)

                if step.name == "get_performance_summary":
                    result = await self.analytics_tools.get_performance_summary(
                        user_id=user_id,
                        system_id=system_id
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

        raise AIInteractionLimitError()