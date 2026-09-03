from fastapi import APIRouter

from app import dependencies as dep


router = APIRouter()

@router.post("/trading-systems/{system_id}/trades")
async def add_trade():
    pass

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