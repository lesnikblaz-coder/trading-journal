from datetime import datetime, timezone, timedelta

from app.core import security
from app.core.config import settings
from app.repositories.user import UserRepo
from app.repositories.refresh_token import RefreshTokenRepo
from app.exceptions.custom import DuplicateEmailError, InvalidCredentialsError
from app.schemas.auth import TokenResponse
from app.database.models.user import User
from app.core.security import decode_access_token
from app.exceptions.custom import UserNotFoundError


class AuthService:
    def __init__(self, repo: UserRepo, refresh_repo: RefreshTokenRepo):
        self.repo = repo
        self.refresh_repo = refresh_repo

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = security.create_access_token(user.id)

        refresh_token = security.create_refresh_token()
        refresh_token_hash = security.hash_refresh_token(refresh_token)

        expire_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await self.refresh_repo.create(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expire_at=expire_at
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )


    async def register(self, email: str, pw: str) -> TokenResponse:
        if await self.repo.get_by_email(email):
            raise DuplicateEmailError()

        user = User(
            email=email,
            hashed_pw=security.get_hash(pw)
        )

        user = await self.repo.create(user)

        return await self._issue_tokens(user)

    async def login(self, email: str, pw: str) -> TokenResponse:
        user = await self.repo.get_by_email(email)

        if not user or not security.verify_pw(pw, user.hashed_pw):
            raise InvalidCredentialsError()

        return await self._issue_tokens(user)

    async def decode_user(self, token: str) -> User | None:
        user_id = decode_access_token(token)
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        return user