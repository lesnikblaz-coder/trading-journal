from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.refresh_token import RefreshToken


class RefreshTokenRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID, token_hash: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        self.session.add(token)
        await self.session.flush()

        return token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
        )

        return result.scalar_one_or_none()

    @staticmethod
    def revoke(token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)