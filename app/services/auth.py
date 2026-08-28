from app import auth
from app.repositories.user import UserRepo
from app.exceptions.custom import DuplicateEmailError, InvalidCredentialsError
from app.schemas.auth import TokenResponse
from app.models.user import User


class AuthService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def register(self, email: str, pw: str) -> TokenResponse:
        if await self.repo.get_by_email(email):
            raise DuplicateEmailError()

        user = User(
            email=email,
            hashed_pw=auth.get_hash(pw)
        )

        user = await self.repo.create(user)

        return TokenResponse(
            access_token=auth.get_token(user.id)
        )

    async def login(self, email: str, pw: str) -> TokenResponse:
        user = await self.repo.get_by_email(email)

        if not user or not auth.verify_pw(pw, user.hashed_pw):
            raise InvalidCredentialsError()

        return TokenResponse(
            access_token=auth.get_token(user.id)
        )