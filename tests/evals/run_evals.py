import asyncio

from uuid import uuid4
from unittest.mock import AsyncMock
from google import genai

from app.core.config import settings
from app.ai.clients.gemini_client import GeminiClient
from app.ai.tools.analytics import AnalyticsTools
from tests.evals.trading_agent_evals import EVAL_CASES


async def main():

    # REAL Gemini SDK
    sdk = genai.Client(api_key=settings.GEMINI_API_KEY)

    # FAKE analytics tools
    analytics_tools = AsyncMock(spec=AnalyticsTools)

    # Fixed evaluation data
    analytics_tools.get_performance_summary.return_value = {
        "total_trades": 100,
        "win_rate": 45.0,
        "avg_winner": 2.0,
        "avg_loser": -1.0,
        "profit_factor": 2.0,
        "expectancy": 0.45,
    }

    analytics_tools.get_performance_by_symbol.return_value = [
        {
            "symbol": "NVDA",
            "total_profit": 5000
        },
        {
            "symbol": "AAPL",
            "total_profit": 2000
        },
        {
            "symbol": "TSLA",
            "total_profit": -1000
        }
    ]

    analytics_tools.get_performance_by_month.return_value = {
        "total_trades": 20,
        "expectancy": 0.28,
        "win_rate": 40,
        "profit_factor": 1.5
    }

    # Real GeminiClient using the real model, but with mocked tools
    agent =  GeminiClient(
        client=sdk.aio,
        analytics_tools=analytics_tools
    )
    system_id, user_id = uuid4(), uuid4()

    try:

        for case in EVAL_CASES[:3]:

            result = await agent.analyze_trading_system(
                question=case["question"],
                system_id=system_id,
                user_id=user_id
            )

            tool_passed = case["expected_tool"] in result.tools_used

            print("\n======================")
            print("QUESTION:", case["question"])
            print("ANSWER:", result.answer)
            print("TOOLS USED:", result.tools_used)
            print("TOOL SELECTION:", tool_passed)

    finally:
        await sdk.aio.aclose()

if __name__ == "__main__":
    asyncio.run(main())