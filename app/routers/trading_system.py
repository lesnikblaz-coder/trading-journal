from uuid import UUID
from fastapi import APIRouter

from app.schemas import trading_system as sc
from app import dependencies as dep


router = APIRouter()


@router.post("/trading-systems", response_model=sc.TradingSystemResponse)
async def create_trading_system(service: dep.TradingSystemServiceDep, request: sc.TradingSystemRequest, user: dep.CurrentUserDep) -> sc.TradingSystemResponse:
    return await service.create(request=request, user_id=user.id)

@router.get("/trading-systems", response_model=list[sc.TradingSystemResponse])
async def get_trading_systems(service: dep.TradingSystemServiceDep, user: dep.CurrentUserDep) -> list[sc.TradingSystemResponse]:
    return await service.get_by_user(user_id=user.id)

@router.get("/trading-systems/{trading_system_id}", response_model=sc.TradingSystemResponse)
async def get_trading_system_by_id(trading_system_id: UUID, service: dep.TradingSystemServiceDep, user: dep.CurrentUserDep) -> sc.TradingSystemResponse | None:
    return await service.get_by_id(trading_system_id=trading_system_id, user_id=user.id)