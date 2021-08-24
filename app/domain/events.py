import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.models import Post


class Event(BaseModel):
    id: str = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.now)


class UserCreationRequested(Event):
    name: str
    password: str


class UserInfoRequested(Event):
    pass


class UserDeletionRequested(Event):
    password: str


class PostCreated(Event):
    user_id: str
    title: str
    content: str


class PostViewRequested(Event):
    pass


class UserPostViewRequested(Event):
    pass


class AllPostViewRequested(Event):
    pass


class PostUpdated(Event):
    new_post: Post


class PostDeleted(Event):
    pass
