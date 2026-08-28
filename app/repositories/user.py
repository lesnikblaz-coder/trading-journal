from sqlalchemy import select

from app.repositories.base import BaseRepo
from app.models.user import User


class UserRepo(BaseRepo[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.email == email)
        )

        return result.scalar_one_or_none()