from typing import Generic, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession



ModelT = TypeVar("ModelT")


class BaseRepo(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.flush(entity)
        return entity