from app.ai.tools.analytics import AnalyticsTools
from app.schemas import ai as sc


def create_tool_registry(analytics_tools: AnalyticsTools) -> dict:
    return {
        "get_performance_summary": (
            analytics_tools.get_performance_summary,
            sc.NoArgs
        ),
        "get_performance_by_month": (
            analytics_tools.get_performance_by_month,
            sc.MonthSummaryArg
        ),
        "get_performance_by_symbol": (
            analytics_tools.get_performance_by_symbol,
            sc.NoArgs
        ),
    }
