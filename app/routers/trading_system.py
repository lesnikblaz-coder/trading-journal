from uuid import UUID
from fastapi import APIRouter

from app import dependencies as dep
from app.schemas import trading_system as sc
from app.database.models.trading_system import TradingSystem


router = APIRouter()


@router.post("/trading-systems", response_model=sc.TradingSystemResponse)
async def create_trading_system(service: dep.TradingSystemServiceDep, request: sc.TradingSystemRequest, user: dep.CurrentUserDep) -> TradingSystem:
    return await service.create(request=request, user_id=user.id)

@router.get("/trading-systems", response_model=list[sc.TradingSystemResponse])
async def get_trading_systems(service: dep.TradingSystemServiceDep, user: dep.CurrentUserDep) -> list[sc.TradingSystemResponse]:
    return await service.get_by_user(user_id=user.id)

@router.get("/trading-systems/{system_id}", response_model=sc.TradingSystemResponse)
async def get_trading_system_by_uuid(trading_system_id: UUID, service: dep.TradingSystemServiceDep, user: dep.CurrentUserDep) -> TradingSystem | None:
    return await service.get_by_id(trading_system_id=trading_system_id, user_id=user.id)

@router.patch("/trading-systems/{system_id}", response_model=sc.TradingSystemResponse)
async def update_trading_system(trading_system_id: UUID, service: dep.TradingSystemServiceDep, request: sc.TradingSystemUpdate, user: dep.CurrentUserDep) -> TradingSystem:
    return await service.update(
        trading_system_id=trading_system_id,
        user_id=user.id,
        update_data=request
    )

@router.delete("/trading-systems/{system_id}", status_code=204)
async def delete_trading_system(trading_system_id: UUID, service: dep.TradingSystemServiceDep, user: dep.CurrentUserDep) -> None:
    return await service.delete_by_id(trading_system_id=trading_system_id, user_id=user.id)