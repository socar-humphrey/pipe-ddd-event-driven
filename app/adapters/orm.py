from datetime import datetime
from typing import Optional

from pypika import Table, Query


class TypedTable(Table):
    __table__ = ""

    def __init__(
            self,
            name: Optional[str] = None,
            schema: Optional[str] = None,
            alias: Optional[str] = None,
            query_cls: Optional[Query] = None,
    ) -> None:
        if name is None:
            if self.__table__:
                name = self.__table__
            else:
                name = self.__class__.__name__

        super().__init__(name, schema, alias, query_cls)


class Users(TypedTable):
    __table__ = "users"

    id: str
    name: str
    password: str
    created_at: datetime
    updated_at: datetime


class Posts(TypedTable):
    __table__ = "posts"

    id: str
    title: str
    content: str
    author: str
    created_at: datetime
    updated_at: datetime


users = Users()
posts = Posts()

users.get_sql()
