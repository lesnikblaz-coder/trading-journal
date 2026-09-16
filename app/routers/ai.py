from uuid import UUID
from fastapi import APIRouter

from app.schemas import ai as sc
from app import dependencies as dep


router = APIRouter()


@router.post("/trades/{trade_id}/ai-review", response_model=sc.AITradeReviewResponse)
async def ai_trade_review(trade_id: UUID, service: dep.TradeReviewServiceDep, user: dep.CurrentUserDep) -> sc.AITradeReviewResponse:
    return await service.generate_trade_review(trade_id, user.id)