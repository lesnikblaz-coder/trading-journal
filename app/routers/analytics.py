from fastapi import APIRouter
from uuid import UUID

from app import dependencies as dep
from app.schemas import analytics as sc


router = APIRouter()


@router.get("/analytics/{system_id}/overview", response_model=sc.AnalyticsOverviewResponse)
async def analytics_overview(system_id: UUID, service: dep.AnalyticsServiceDep, user: dep.CurrentUserDep) -> sc.AnalyticsOverviewResponse:
    return await service.overview(trading_system_id=system_id, user_id=user.id)