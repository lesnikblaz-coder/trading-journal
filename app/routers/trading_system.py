from fastapi import APIRouter

from app.schemas import trading_system as sc
from app import dependencies as dep


router = APIRouter()


@router.post("/trading-systems", response_model=sc.TradingSystemResponse)
async def create_trading_system(service: dep.TradingSystemServiceDep, request: sc.TradingSystemRequest, user: dep.CurrentUserDep):
    return await service.create(request=request, user_id=user.id)