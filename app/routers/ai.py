from uuid import UUID
from fastapi import APIRouter

from app.schemas import ai as sc
from app import dependencies as dep


router = APIRouter(
    dependencies=[
        dep.AiRateLimitDep
    ]
)


@router.post("/trades/{trade_id}/ai-review", response_model=sc.AITradeReviewResponse)
async def ai_trade_review(trade_id: UUID, service: dep.TradeReviewServiceDep, user: dep.CurrentUserDep) -> sc.AITradeReviewResponse:
    return await service.generate_trade_review(trade_id, user.id)

@router.post("/trading-systems/{system_id}/ai-analysis", response_model=sc.AIAnalysisResponse)
async def ai_trading_system_analysis(system_id: UUID, request: sc.AIAnalysisRequest, client: dep.GeminiClientDep, user: dep.CurrentUserDep) -> sc.AIAnalysisResponse:
    return await client.analyze_trading_system(
        question=request.question,
        system_id=system_id,
        user_id=user.id
    )