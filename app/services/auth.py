from app.core import security
from app.repositories.user import UserRepo
from app.exceptions.custom import DuplicateEmailError, InvalidCredentialsError
from app.schemas.auth import TokenResponse
from app.database.models.user import User
from app.core.security import decode_access_token
from app.exceptions.custom import UserNotFoundError


class AuthService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def register(self, email: str, pw: str) -> TokenResponse:
        if await self.repo.get_by_email(email):
            raise DuplicateEmailError()

        user = User(
            email=email,
            hashed_pw=security.get_hash(pw)
        )

        user = await self.repo.create(user)

        return TokenResponse(
            access_token=security.create_access_token(user.id)
        )

    async def login(self, email: str, pw: str) -> TokenResponse:
        user = await self.repo.get_by_email(email)

        if not user or not security.verify_pw(pw, user.hashed_pw):
            raise InvalidCredentialsError()

        return TokenResponse(
            access_token=security.create_access_token(user.id)
        )

    async def decode_user(self, token: str) -> User | None:
        user_id = decode_access_token(token)
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise UserNotFoundError()

        return user