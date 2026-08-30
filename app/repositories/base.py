from typing import Generic, TypeVar, Sequence, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession



ModelT = TypeVar("ModelT")


class BaseRepo(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_all(self) -> Sequence[ModelT]:
        result = await self.session.execute(select(self.model))

        return result.scalars().all()

    async def get_by_id(self, entity_id: int) -> ModelT | None:
        result = await self.session.execute(
            select(self.model)
            .where(self.model.id == entity_id)
        )

        return result.scalar_one_or_none()

    async def update(self, entity_id: int, **fields: Any) -> ModelT | None:
        entity = await self.get_by_id(entity_id)

        if entity is None:
            return None

        for field, value in fields.items():
            setattr(entity, field, value)

        await self.session.flush()

        return entity

    async def delete(self, entity_id: int) -> ModelT | None:
        entity = await self.get_by_id(entity_id)

        if entity is None:
            return None

        entity = await self.session.delete(entity)

        return entity