from uuid import UUID

from app.repositories.trading_system import TradingSystemRepo
from app.database.models.trading_system import TradingSystem
from app.schemas.trading_system import TradingSystemRequest, TradingSystemResponse


class TradingSystemService:
    def __init__(self, trading_system_repo: TradingSystemRepo):
        self.repo = trading_system_repo

    async def create(self, request: TradingSystemRequest, user_id: UUID) -> TradingSystemResponse:

        trading_system = TradingSystem(
            user_id=user_id,
            **request.model_dump(exclude_none=True)
        )

        return await self.repo.create(trading_system)

    async def get_by_user(self, user_id: UUID) -> list[TradingSystemResponse]:
        result = await self.repo.get_by_user(user_id)

        return [TradingSystemResponse.model_validate(r) for r in result]

    async def get_by_id(self, trading_system_id: UUID, user_id: UUID) -> TradingSystemResponse | None:
        return await self.repo.get_by_id(
            entity_id=trading_system_id,
            user_id=user_id
        )