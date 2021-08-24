from abc import ABC, abstractmethod

import databases

from app.adapters.repository import UserRepository, PostRepository, Repository


class UnitOfWork(ABC):
    users = Repository()
    posts = Repository()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.rollback()

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class AsyncORMUnitOfWork(UnitOfWork):
    def __init__(self, database: databases.Database):
        self.database = database

    async def __aenter__(self):
        self.users = UserRepository(self.database)
        self.posts = PostRepository(self.database)
        await self.database.transaction().start()
        return super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)

    async def commit(self):
        await self.database.transaction().commit()

    async def rollback(self):
        await self.database.transaction().rollback()
