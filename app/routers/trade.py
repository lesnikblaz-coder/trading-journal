from uuid import UUID
from fastapi import APIRouter

from app import dependencies as dep
from app.schemas import trade as sc


router = APIRouter()

@router.post("/trading-systems/{system_id}/trades", response_model=sc.TradeResponse)
async def add_trade(system_id: UUID, request: sc.TradeCreateRequest, service: dep.TradeServiceDep, user: dep.CurrentUserDep) -> sc.TradeResponse:
    return await service.create(system_id, request, user.id)

@router.get("/trading-systems/{system_id}/trades", response_model=list[sc.TradeResponse])
async def get_user_trades(system_id: UUID, service: dep.TradeServiceDep, user: dep.CurrentUserDep) -> list[sc.TradeResponse]:
    return await service.get_all_for_system(system_id, user.id)

@router.get("/trades/{trade_id}", response_model=sc.TradeResponse)
async def get_trade_by_id(trade_id: UUID, service: dep.TradeServiceDep, user: dep.CurrentUserDep) -> sc.TradeResponse | None:
    return await service.get_by_id(trade_id, user.id)

@router.patch("/trades/{trade_id}", response_model=sc.TradeResponse)
async def update_trade(trade_id: UUID, request: sc.TradeUpdateRequest, service: dep.TradeServiceDep, user: dep.CurrentUserDep) -> sc.TradeResponse:
    return await service.update(trade_id, user.id, request)

@router.delete("/trades/{trade_id}", status_code=204)
async def delete_trade(trade_id: UUID, service: dep.TradeServiceDep, user: dep.CurrentUserDep) -> None:
    return await service.delete(trade_id, user.id)