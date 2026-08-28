from sqlalchemy.ext.asyncio import AsyncSession


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self):