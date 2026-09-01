from fastapi import Depends
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import AsyncSessionLocal
from app.services.trading_system import TradingSystemService
from app.repositories.trading_system import TradingSystemRepo
from app.repositories.user import UserRepo
from app.services.auth import AuthService
from app.database.models.user import User
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

async def _get_auth_service(repo: UserRepoDep) -> AuthService:
    return AuthService(repo)

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