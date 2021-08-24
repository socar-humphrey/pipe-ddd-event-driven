from typing import List

from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    id: str
    name: str
    password: str


class UserDeletionRequest(BaseModel):
    password: str


class PostCreationRequest(BaseModel):
    user_id: str
    user_password: str
    title: str
    content: str


class PostCreationResponse(BaseModel):
    user_id: str = Field(alias="author")
    id: str
    title: str
    content: str


class UserPost(BaseModel):
    user_id: str
    user_name: str
    id: str
    title: str
    content: str


class UserPosts(BaseModel):
    items: List[UserPost]


class NewPostRequest(BaseModel):
    user_id: str
    user_password: str
    title: str
    content: str