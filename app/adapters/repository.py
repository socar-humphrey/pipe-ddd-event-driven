from abc import ABC, abstractmethod
from typing import List, Tuple, Callable

import databases

from pypika import Query
from app.adapters.orm import users, posts
from app.domain.models import User, Model, Post


class RepositoryError(Exception):
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code

    def __str__(self):
        return f"{self.__class__.__name__}({self.code}): {self.message}"


class InsertFailureError(RepositoryError):
    pass


class Repository(ABC):
    @abstractmethod
    def get_by_id(self, _id: str) -> ...:
        ...

    @abstractmethod
    async def get_by_id(self, _id: str) -> ...:
        ...

    @abstractmethod
    def add(self, entity: ...) -> ...:
        ...

    @abstractmethod
    async def add(self, entity: ...) -> ...:
        ...


class ORMRepository(Repository):
    def __init__(self, database: databases.Database):
        self.database = database

    def build_model(self, model: Callable[..., Model], columns: List[str], record: Tuple) -> Model:
        return model(**{col: record[idx] for idx, col in enumerate(columns)})

    def extract_columns_and_values(self, entity: Model):
        return zip(*entity.dict(by_alias=True).items())

    async def get_by_id(self, _id: str) -> ...:
        return await self._get_by_id(_id=_id)

    @abstractmethod
    async def _get_by_id(self, _id: str) -> ...:
        ...

    async def add(self, entity: ...) -> ...:
        return await self._add(entity=entity)

    @abstractmethod
    async def _add(self, entity: ...) -> ...:
        ...


class UserRepository(ORMRepository):
    async def _get_by_id(self, _id: str) -> User:
        columns = ["id", "name", "password"]
        query = Query.from_(users).select(*columns).where(users.id == _id)
        result = await self.database.fetch_one(query=query.get_sql())
        return self.build_model(User, columns=columns, record=result)

    async def _add(self, entity: User) -> None:
        columns, values = self.extract_columns_and_values(entity)
        query = Query.into(users).columns(*columns).insert(*values)
        result = await self.database.execute(query.get_sql())
        if result == -1:
            raise InsertFailureError(message=f"INSERT에 실패했습니다 [{entity}]")


class PostRepository(ORMRepository):
    def __init__(self, database: databases.Database):
        super().__init__(database=database)
        self.user_repository = UserRepository(self.database)

    async def _get_by_id(self, _id: str) -> Post:
        columns = ["id", "title", "content", "author"]
        query = Query.from_(users).select(*columns).where(users.id == _id)
        result = await self.database.fetch_one(query=query.get_sql())
        return self.build_model(User, columns=columns, record=result)

    async def _add(self, entity: Post) -> None:
        author_entity = await self.user_repository.get_by_id(entity.author.id_)
        entity.author = author_entity.id_
        columns, values = self.extract_columns_and_values(entity)
        query = Query.into(posts).columns(*columns).insert(*values)
        result = await self.database.execute(query.get_sql())
        if result == -1:
            raise InsertFailureError(message=f"INSERT에 실패했습니다 [{entity}]")


if __name__ == '__main__':
    import asyncio

    database = databases.Database("sqlite:///./test.db")
    repo = UserRepository(database=database)
    posts_repo = PostRepository(database=database)


    async def get_item(_id: str):
        result = await repo.get_by_id(_id)
        print(result)


    async def add_item(user: User):
        await repo.add(entity=user)


    async def add_post(post: Post):
        await posts_repo.add(post)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        add_post(Post(id="hello", title="humphrey", content="woerhowehrowerno", author=User(id="humphrey", name="humphrey", password="humphrey"))))
    loop.close()
