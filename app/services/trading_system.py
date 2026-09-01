from uuid import UUID

from app.repositories.trading_system import TradingSystemRepo
from app.database.models.trading_system import TradingSystem
from app.schemas.trading_system import TradingSystemRequest


class TradingSystemService:
    def __init__(self, trading_system_repo: TradingSystemRepo):
        self.repo = trading_system_repo

    async def create(self, request: TradingSystemRequest, user_id: UUID):

        request_dict = request.model_dump(exclude_none=True)

        request_dict["user_id"] = user_id

        trading_system = TradingSystem(**request_dict)

        return await self.repo.create(trading_system)