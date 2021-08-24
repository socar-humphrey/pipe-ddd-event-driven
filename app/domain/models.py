from typing import Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Model(BaseModel):
    id_: Union[UUID, str] = Field(default_factory=uuid4, alias="id")


class User(Model):
    name: str
    password: str


class Post(Model):
    title: str
    author: Union[User, str]
    content: str = Field(max_length=200)
