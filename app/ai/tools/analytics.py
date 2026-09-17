from uuid import UUID

from app.services.analytics import AnalyticsService


class AnalyticsTools:
    def __init__(self, analytics_service: AnalyticsService):
        self.analytics_service = analytics_service

    async def get_performance_summary(self, system_id: UUID, user_id: UUID) -> dict:
        result = await self.analytics_service.overview_by_system_id(
            trading_system_id=system_id,
            user_id=user_id
        )

        return result.model_dump()

    async def get_performance_by_month(self, year: int, month: int, user_id: UUID) -> dict:
        result = await self.analytics_service.overview_monthly_performance(
            year=year,
            month=month,
            user_id=user_id
        )

        return result.model_dump()

    async def get_performance_by_symbol(self, symbol: str, user_id: UUID) -> dict:
        result = await self.analytics_service.overview_by_symbol(
            symbol=symbol,
            user_id=user_id
        )

        return result.model_dump()