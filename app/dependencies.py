from fastapi import Depends
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.repositories.user import UserRepo
from app.services.auth import AuthService


# ---------- SESSION ----------
async def _get_session():
    async with AsyncSessionLocal() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(_get_session)]



# ---------- USER ----------
async def _get_user_repo(session: SessionDep) -> UserRepo:
    return UserRepo(session)

UserRepoDep = Annotated[UserRepo, Depends(_get_user_repo)]



# ---------- AUTH ----------
async def _get_auth_service(repo: UserRepoDep) -> AuthService:
    return AuthService(repo)

AuthServiceDep = Annotated[AuthService, Depends(_get_auth_service)]