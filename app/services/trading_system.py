from uuid import UUID

from app.repositories.trading_system import TradingSystemRepo
from app.database.models.trading_system import TradingSystem
from app.schemas import trading_system as sc


class TradingSystemService:
    def __init__(self, trading_system_repo: TradingSystemRepo):
        self.repo = trading_system_repo

    async def create(self, request: sc.TradingSystemRequest, user_id: UUID) -> sc.TradingSystemResponse:

        trading_system = TradingSystem(
            user_id=user_id,
            **request.model_dump(exclude_none=True)
        )

        return await self.repo.create(trading_system)

    async def get_by_user(self, user_id: UUID) -> list[sc.TradingSystemResponse]:
        result = await self.repo.get_by_user(user_id)

        return [sc.TradingSystemResponse.model_validate(r) for r in result]

    async def get_by_id(self, trading_system_id: UUID, user_id: UUID) -> sc.TradingSystemResponse | None:
        return await self.repo.get_by_id(
            entity_id=trading_system_id,
            user_id=user_id
        )

    async def update(self, trading_system_id: UUID, user_id: UUID, update_data: sc.TradingSystemUpdate) -> sc.TradingSystemResponse:
        return await self.repo.update(
            entity_id=trading_system_id,
            user_id=user_id,
            update_data=update_data.model_dump(exclude_none=True)
        )

    async def delete_by_id(self, trading_system_id: UUID, user_id: UUID) -> None:
        return await self.repo.delete(
            entity_id=trading_system_id,
            user_id=user_id
        )