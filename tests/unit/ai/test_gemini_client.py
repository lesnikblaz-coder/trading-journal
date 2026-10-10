import pytest
import json
import pydantic

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from google import genai

from app.ai.clients.gemini_client import GeminiClient
from app.ai.tools.analytics import AnalyticsTools


@pytest.fixture
def mock_analytics_tools():
    return AsyncMock(spec=AnalyticsTools)

@pytest.fixture
def mock_gemini_sdk():
    client = MagicMock(spec=genai.client.AsyncClient)
    client.interactions.create = AsyncMock()
    return client

@pytest.fixture
def gemini_client(
        mock_gemini_sdk,
        mock_analytics_tools
):
    return GeminiClient(
        client=mock_gemini_sdk,
        analytics_tools=mock_analytics_tools
    )


# TESTS
async def test_analyze_without_tool_calls(
        gemini_client,
        mock_gemini_sdk,
        mock_analytics_tools
):
    system_id, user_id = uuid4(), uuid4()

    fake_response = SimpleNamespace(
        id="interaction-1",
        steps=[],
        output_text="Hello! How can I help?"
    )

    mock_gemini_sdk.interactions.create.return_value = fake_response

    result = await gemini_client.analyze_trading_system(
        question="Hello",
        system_id=system_id,
        user_id=user_id
    )

    assert result.answer == "Hello! How can I help?"
    assert result.tools_used == []

    mock_gemini_sdk.interactions.create.assert_awaited_once()

    mock_analytics_tools.get_performance_summary.assert_not_awaited()
    mock_analytics_tools.get_performance_by_month.assert_not_awaited()
    mock_analytics_tools.get_performance_by_symbol.assert_not_awaited()

async def test_analyze_one_tool_call(
        gemini_client,
        mock_gemini_sdk,
        mock_analytics_tools
):
    system_id, user_id = uuid4(), uuid4()

    first_response = SimpleNamespace(
        id="interaction-1",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="get_performance_summary",
                id="abc-123",
                arguments={}
            )
        ],
        output_text=None
    )

    second_response = SimpleNamespace(
        id="interaction-2",
        steps=[],
        output_text="Your trading system currently has positive expectancy."
    )

    mock_analytics_tools.get_performance_summary.return_value = {
        "expectancy": 0.48,
        "total_trades": 500
    }

    mock_gemini_sdk.interactions.create.side_effect = [
        first_response,
        second_response
    ]

    result = await gemini_client.analyze_trading_system(
        question="Am I profitable?",
        system_id=system_id,
        user_id=user_id
    )

    assert result.answer == "Your trading system currently has positive expectancy."
    assert len(result.tools_used) == 1
    assert result.tools_used[0] == "get_performance_summary"

    mock_analytics_tools.get_performance_summary.assert_awaited_once_with(
        system_id=system_id,
        user_id=user_id
    )

    assert mock_gemini_sdk.interactions.create.await_count == 2

    last_call = mock_gemini_sdk.interactions.create.await_args_list[1]
    tool_result = last_call.kwargs["input"][0]
    result_text = tool_result["result"][0]["text"]

    parsed_result = json.loads(result_text)

    assert parsed_result["expectancy"] == 0.48
    assert parsed_result["total_trades"] == 500

async def test_analyze_multiple_tool_calls(
        gemini_client,
        mock_gemini_sdk,
        mock_analytics_tools
):
    system_id, user_id = uuid4(), uuid4()

    first_response = SimpleNamespace(
        id="interaction-1",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="get_performance_summary",
                id="call-1",
                arguments={}
            ),
            SimpleNamespace(
                type="function_call",
                name="get_performance_by_symbol",
                id="call-2",
                arguments={}
            ),
        ],
        output_text=None
    )

    second_response = SimpleNamespace(
        id="interaction-2",
        steps=[],
        output_text="Your system is profitable, and NVDA is your best symbol."
    )

    mock_analytics_tools.get_performance_summary.return_value = {
        "expectancy": 0.48,
        "total_trades": 500
    }

    mock_analytics_tools.get_performance_by_symbol.return_value = [
        {
            "symbol": "NVDA",
            "total_profit": 5000
        },
        {
            "symbol": "AAPL",
            "total_profit": 2000
        }
    ]

    mock_gemini_sdk.interactions.create.side_effect = [
        first_response,
        second_response
    ]

    result = await gemini_client.analyze_trading_system(
        question="Am I profitable?",
        system_id=system_id,
        user_id=user_id
    )

    assert result.answer == "Your system is profitable, and NVDA is your best symbol."
    assert len(result.tools_used) == 2
    assert result.tools_used == [
        "get_performance_summary",
        "get_performance_by_symbol"
    ]

    mock_analytics_tools.get_performance_summary.assert_awaited_once_with(
        user_id=user_id,
        system_id=system_id
    )
    mock_analytics_tools.get_performance_by_symbol.assert_awaited_once_with(
        user_id=user_id,
        system_id=system_id
    )

    assert mock_gemini_sdk.interactions.create.await_count == 2

    last_call = mock_gemini_sdk.interactions.create.await_args_list[1]

    assert last_call.kwargs["previous_interaction_id"] == "interaction-1"

    function_results = last_call.kwargs["input"]

    assert len(function_results) == 2
    assert function_results[0]["call_id"] == "call-1"
    assert function_results[0]["type"] == "function_result"
    assert function_results[0]["name"] == "get_performance_summary"

    assert function_results[1]["call_id"] == "call-2"
    assert function_results[1]["type"] == "function_result"
    assert function_results[1]["name"] == "get_performance_by_symbol"

    result_text_1 = function_results[0]["result"][0]["text"]
    result_text_2 = function_results[1]["result"][0]["text"]

    parsed_result_1 = json.loads(result_text_1)
    parsed_result_2 = json.loads(result_text_2)

    assert parsed_result_1["expectancy"] == 0.48
    assert parsed_result_1["total_trades"] == 500

    assert parsed_result_2[0]["symbol"] == "NVDA"
    assert parsed_result_2[0]["total_profit"] == 5000

    assert parsed_result_2[1]["symbol"] == "AAPL"
    assert parsed_result_2[1]["total_profit"] == 2000

async def test_analyze_sequential_tool_calls(
        gemini_client,
        mock_gemini_sdk,
        mock_analytics_tools
):
    system_id, user_id = uuid4(), uuid4()

    first_response = SimpleNamespace(
        id="interaction-1",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="get_performance_summary",
                id="call-1",
                arguments={}
            )
        ],
        output_text=None
    )

    second_response = SimpleNamespace(
        id="interaction-2",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="get_performance_by_month",
                id="call-2",
                arguments={
                    "year": 2026,
                    "month": 9
                }
            )
        ],
        output_text=None
    )

    third_response = SimpleNamespace(
        id="interaction-3",
        steps=[],
        output_text="Your system is profitable overall, but September was weaker."
    )

    mock_analytics_tools.get_performance_summary.return_value = {
        "expectancy": 0.48,
        "total_trades": 500
    }

    mock_analytics_tools.get_performance_by_month.return_value = {
        "expectancy": 0.28,
        "total_trades": 20
    }

    mock_gemini_sdk.interactions.create.side_effect = [
        first_response,
        second_response,
        third_response
    ]

    result = await gemini_client.analyze_trading_system(
        question="Am I profitable overall, and how did I perform in September 2026?",
        system_id=system_id,
        user_id=user_id
    )

    assert result.answer == "Your system is profitable overall, but September was weaker."
    assert len(result.tools_used) == 2
    assert result.tools_used == [
        "get_performance_summary",
        "get_performance_by_month"
    ]

    mock_analytics_tools.get_performance_summary.assert_awaited_once_with(
        user_id=user_id,
        system_id=system_id
    )
    mock_analytics_tools.get_performance_by_month.assert_awaited_once_with(
        user_id=user_id,
        system_id=system_id,
        year=2026,
        month=9
    )

    assert mock_gemini_sdk.interactions.create.await_count == 3

    calls = mock_gemini_sdk.interactions.create.await_args_list

    assert calls[1].kwargs["previous_interaction_id"] == "interaction-1"
    assert calls[2].kwargs["previous_interaction_id"] == "interaction-2"

    function_result_1 = calls[1].kwargs["input"]
    function_result_2 = calls[2].kwargs["input"]

    assert function_result_1[0]["call_id"] == "call-1"
    assert function_result_1[0]["type"] == "function_result"
    assert function_result_1[0]["name"] == "get_performance_summary"

    assert function_result_2[0]["call_id"] == "call-2"
    assert function_result_2[0]["type"] == "function_result"
    assert function_result_2[0]["name"] == "get_performance_by_month"

    result_text_1 = function_result_1[0]["result"][0]["text"]
    result_text_2 = function_result_2[0]["result"][0]["text"]

    parsed_result_1 = json.loads(result_text_1)
    parsed_result_2 = json.loads(result_text_2)

    assert parsed_result_1["expectancy"] == 0.48
    assert parsed_result_1["total_trades"] == 500

    assert parsed_result_2["expectancy"] == 0.28
    assert parsed_result_2["total_trades"] == 20

async def test_analyze_unknown_tool_call(
        gemini_client,
        mock_gemini_sdk,
        mock_analytics_tools
):
    system_id, user_id = uuid4(), uuid4()

    response = SimpleNamespace(
        id="interaction-1",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="delete_all_trades",
                id="call-123",
                arguments={}
            )
        ],
        output_text=None
    )

    mock_gemini_sdk.interactions.create.return_value = response

    with pytest.raises(ValueError, match="Unknown function call"):
        await gemini_client.analyze_trading_system(
            question="Delete everything",
            system_id=system_id,
            user_id=user_id
        )

    mock_gemini_sdk.interactions.create.assert_awaited_once()

    mock_analytics_tools.get_performance_summary.assert_not_awaited()
    mock_analytics_tools.get_performance_by_month.assert_not_awaited()
    mock_analytics_tools.get_performance_by_symbol.assert_not_awaited()

async def test_invalid_arguments(
        gemini_client,
        mock_gemini_sdk,
        mock_analytics_tools
):
    system_id, user_id = uuid4(), uuid4()

    response = SimpleNamespace(
        id="interaction-1",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="get_performance_by_month",
                id="call-123",
                arguments={
                    "year": "banana",
                    "month": "September"
                }
            )
        ],
        output_text=None
    )

    mock_gemini_sdk.interactions.create.return_value = response

    with pytest.raises(pydantic.ValidationError):
        await gemini_client.analyze_trading_system(
            question="What was my performance in September? I love bananas!",
            system_id=system_id,
            user_id=user_id
        )

    mock_gemini_sdk.interactions.create.assert_awaited_once()

    mock_analytics_tools.get_performance_summary.assert_not_awaited()
    mock_analytics_tools.get_performance_by_month.assert_not_awaited()
    mock_analytics_tools.get_performance_by_symbol.assert_not_awaited()