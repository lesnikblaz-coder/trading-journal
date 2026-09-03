from uuid import UUID
from fastapi import APIRouter

from app import dependencies as dep
from app.schemas import trade as sc


router = APIRouter()

@router.post("/trading-systems/{system_id}/trades")
async def add_trade(system_id: UUID, request: sc.TradeCreateRequest, service: dep.TradeServiceDep, user: dep.CurrentUserDep):
    return await service.create(
        system_id,
        request,
        user.id
    )

@router.get("/trading-systems/{system_id}/trades")
async def get_user_trades():
    pass

@router.get("/trades/{trade_id}")
async def get_trade_by_id():
    pass

@router.patch("/trades/{trade_id}")
async def update_trade():
    pass

@router.delete("/trades/{trade_id}")
async def delete_trade():
    pass