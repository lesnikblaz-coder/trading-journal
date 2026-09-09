from fastapi import APIRouter
from uuid import UUID

from app import dependencies as dep
from app.schemas import analytics as sc


router = APIRouter()


@router.get("/analytics/{system_id}/overview", response_model=sc.AnalyticsOverviewResponse)
async def analytics_overview(system_id: UUID, service: dep.AnalyticsServiceDep, user: dep.CurrentUserDep) -> sc.AnalyticsOverviewResponse:
    return await service.overview_by_system_id(trading_system_id=system_id, user_id=user.id)

@router.post("/analytics/perfromance/month", response_model=sc.AnalyticsOverviewResponse)
async def monthly_performance(service: dep.AnalyticsServiceDep, request: sc.PerformanceRequest, user: dep.CurrentUserDep) -> sc.AnalyticsOverviewResponse:
    return await service.overview_monthly_performance(request.year, request.month, user.id)