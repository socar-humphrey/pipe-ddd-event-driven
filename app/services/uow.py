from abc import ABC, abstractmethod

import databases

from app.adapters.repository import UserRepository, PostRepository, Repository


class UnitOfWork(ABC):
    users = None
    posts = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()
        # pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class AsyncORMUnitOfWork(UnitOfWork):
    def __init__(self, database: databases.Database):
        self.database = database
        self.transaction = self.database.transaction()

    async def __aenter__(self):
        self.users = UserRepository(self.database)
        self.posts = PostRepository(self.database)
        await self.transaction.start()
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)

    async def commit(self):
        await self.transaction.commit()

    async def rollback(self):
        # await self.transaction.rollback()
        pass
