from abc import ABC, abstractmethod
from typing import List, Tuple, Callable

import databases

from pypika import Query, JoinType
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


class DeleteFailureError(RepositoryError):
    pass


class EntityNotFoundError(RepositoryError):
    def __init__(self, message: str):
        super().__init__(message=message, code=404)


class Repository(ABC):
    @abstractmethod
    async def get_by_id(self, _id: str) -> ...:
        ...

    @abstractmethod
    async def add(self, entity: ...) -> ...:
        ...

    @abstractmethod
    async def delete(self, _id: str) -> ...:
        ...

    @abstractmethod
    async def update(self, _id: str, new_entity: ...) -> ...:
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

    async def delete(self, _id: str) -> ...:
        await self._delete(_id=_id)

    @abstractmethod
    async def _delete(self, _id: str) -> ...:
        ...

    async def update(self, _id: str, new_entity: ...) -> ...:
        await self._update(_id, new_entity)

    @abstractmethod
    async def _update(self, _id: str, new_entity: ...) -> ...:
        ...


class UserRepository(ORMRepository):
    async def _get_by_id(self, _id: str) -> User:
        columns = ["id", "name", "password"]
        query = Query.from_(users).select(*columns).where(users.id == _id)
        result = await self.database.fetch_one(query=query.get_sql())
        if not result:
            raise EntityNotFoundError(message=f"User 엔티티를 찾을 수 없습니다 [id: {_id}]")
        return self.build_model(User, columns=columns, record=result)

    async def _add(self, entity: User) -> None:
        columns, values = self.extract_columns_and_values(entity)
        query = Query.into(users).columns(*columns).insert(*values)
        result = await self.database.execute(query.get_sql())
        if result == -1:
            raise InsertFailureError(message=f"INSERT에 실패했습니다 [{entity}]")

    async def _delete(self, _id: str) -> User:
        async with self.database.transaction():
            found_user = await self._get_by_id(_id)
            query = Query.from_(users).delete().where(users.id == found_user.id_)
            result = await self.database.execute(query=query.get_sql())
            if result == -1:
                raise DeleteFailureError(message=f"DELETE에 실패했습니다 [user_id: {_id}]")
            return found_user

    async def _update(self, _id: str, new_entity: User) -> User:
        async with self.database.transaction():
            found_user = await self._get_by_id(_id)
            columns, values = self.extract_columns_and_values(new_entity)
            query = users.update().where(users.id == found_user.id_)
            for i in range(len(columns)):
                query = query.set(columns[i], values[i])
            result = await self.database.execute(query=query.get_sql())
            if result == -1:
                raise
            return self.build_model(User, columns, values)

    async def get_user_posts(self, _id: str):
        async with self.database.transaction():
            await self._get_by_id(_id)
            query = Query.from_(posts).join(users, JoinType.inner).on(posts.author == users.id).get_sql()
            rows = await self.database.fetch_all(query)
            return rows


class PostRepository(ORMRepository):
    def __init__(self, database: databases.Database):
        super().__init__(database=database)
        self.user_repository = UserRepository(self.database)

    async def _get_by_id(self, _id: str) -> Post:
        columns = ["id", "title", "content", "author"]
        query = Query.from_(users).select(*columns).where(users.id == _id)
        result = await self.database.fetch_one(query=query.get_sql())
        if not result:
            raise EntityNotFoundError(message=f"Post 엔티티를 찾을 수 없습니다 [id: {_id}]")
        return self.build_model(User, columns=columns, record=result)

    async def _add(self, entity: Post) -> None:
        author_entity = await self.user_repository.get_by_id(entity.author.id_)
        entity.author = author_entity.id_
        columns, values = self.extract_columns_and_values(entity)
        query = Query.into(posts).columns(*columns).insert(*values)
        result = await self.database.execute(query.get_sql())
        if result == -1:
            raise InsertFailureError(message=f"INSERT에 실패했습니다 [{entity}]")

    async def _delete(self, _id: str) -> Post:
        found_post = await self._get_by_id(_id)
        query = Query.from_(posts).delete().where(posts.id == found_post.id_)
        result = await self.database.execute(query=query.get_sql())
        if result == -1:
            raise DeleteFailureError(message=f"DELETE에 실패했습니다 [user_id: {_id}]")
        return found_post

    async def _update(self, _id: str, new_entity: Post) -> Post:
        found_post = await self._get_by_id(_id)
        columns, values = self.extract_columns_and_values(new_entity)
        query = posts.update().where(posts.id == found_post.id_)
        for i in range(len(columns)):
            query = query.set(columns[i], values[i])
        result = await self.database.execute(query=query.get_sql())
        if result == -1:
            raise
        return self._get_by_id(_id)  # use transactions

    async def get_all(self) -> List[Post]:
        columns = ['id', 'title', 'content']
        query = posts.select(*columns).get_sql()
        rows = await self.database.fetch_all(query=query)
        return [self.build_model(Post, columns, row) for row in rows]


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


    async def update_user(_id: str, new_user: User):
        result = await repo.update(_id, new_user)
        print(result)


    async def delete_user(_id: str):
        result = await repo.delete(_id)
        print(result)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(add_item(User(id="humphrey", name="humphrey", password="humphrey")))
    loop.run_until_complete(
        update_user(_id="humphrey", new_user=User(id="humphrey", name="new humphrey", password="new humphrey")))
    loop.run_until_complete(delete_user(_id="humphrey"))
    loop.close()
