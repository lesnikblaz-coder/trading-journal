from fastapi import Depends, Request
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession


from app.database.base import AsyncSessionLocal
from app.database.models.user import User

from app.services.trading_system import TradingSystemService
from app.services.auth import AuthService
from app.services.trade import TradeService
from app.services.analytics import AnalyticsService
from app.services.trade_review import TradeReviewService

from app.repositories.trading_system import TradingSystemRepo
from app.repositories.user import UserRepo
from app.repositories.trade import TradeRepo
from app.repositories.refresh_token import RefreshTokenRepo

from app.ai.clients.gemini_client import GeminiClient
from app.ai.tools.analytics import AnalyticsTools

from app.core.security import oauth2_scheme


# ---------- SESSION ----------
async def _get_session():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session

SessionDep = Annotated[AsyncSession, Depends(_get_session)]



# ---------- USER ----------
async def _get_user_repo(session: SessionDep) -> UserRepo:
    return UserRepo(session)

UserRepoDep = Annotated[UserRepo, Depends(_get_user_repo)]


# ---------- AUTH ----------
TokenDep = Annotated[str, Depends(oauth2_scheme)]

async def _get_refresh_token_repo(session: SessionDep) -> RefreshTokenRepo:
    return RefreshTokenRepo(session)

RefreshTokenRepoDep = Annotated[RefreshTokenRepo, Depends(_get_refresh_token_repo)]


async def _get_auth_service(repo: UserRepoDep, refresh_repo: RefreshTokenRepoDep) -> AuthService:
    return AuthService(repo, refresh_repo)

AuthServiceDep = Annotated[AuthService, Depends(_get_auth_service)]


async def _get_current_user(token: TokenDep, auth_service: AuthServiceDep) -> User | None:
    return await auth_service.decode_user(token)


CurrentUserDep = Annotated[User, Depends(_get_current_user)]


# ---------- TRADING SYSTEM ----------
async def _get_trading_system_repo(session: SessionDep) -> TradingSystemRepo:
    return TradingSystemRepo(session)

TradingSystemRepoDep = Annotated[TradingSystemRepo, Depends(_get_trading_system_repo)]

async def _get_trading_system_service(repo: TradingSystemRepoDep) -> TradingSystemService:
    return TradingSystemService(repo)

TradingSystemServiceDep = Annotated[TradingSystemService, Depends(_get_trading_system_service)]


# ---------- TRADE ----------
async def _get_trade_repo(session: SessionDep) -> TradeRepo:
    return TradeRepo(session)

TradeRepoDep = Annotated[TradeRepo, Depends(_get_trade_repo)]


async def _get_trade_service(t_repo: TradeRepoDep, t_s_repo: TradingSystemRepoDep) -> TradeService:
    return TradeService(
        t_repo,
        t_s_repo
    )

TradeServiceDep = Annotated[TradeService, Depends(_get_trade_service)]


# ---------- ANALYTICS ----------
async def _get_analytics_service(trade_repo: TradeRepoDep) -> AnalyticsService:
    return AnalyticsService(trade_repo)

AnalyticsServiceDep = Annotated[AnalyticsService, Depends(_get_analytics_service)]


# ---------- AI CLIENT ----------
async def _get_gemini_client(request: Request, analytics_tools: AnalyticsToolsDep, trading_system_repo: TradingSystemRepoDep) -> GeminiClient:
    return GeminiClient(
        client=request.app.state.gemini,
        analytics_tools=analytics_tools,
        trading_system_repo=trading_system_repo
    )

GeminiClientDep = Annotated[GeminiClient, Depends(_get_gemini_client)]


# ---------- AI ----------
async def _get_analytics_tools(analytics_service: AnalyticsServiceDep) -> AnalyticsTools:
    return AnalyticsTools(analytics_service=analytics_service)

AnalyticsToolsDep = Annotated[AnalyticsTools, Depends(_get_analytics_tools)]


async def _get_trade_review_service(client: GeminiClientDep, trade_repo: TradeRepoDep) -> TradeReviewService:
    return TradeReviewService(
        client=client,
        trade_repo=trade_repo
    )

TradeReviewServiceDep = Annotated[TradeReviewService, Depends(_get_trade_review_service)]