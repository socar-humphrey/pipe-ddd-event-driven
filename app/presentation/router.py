import http

from fastapi import APIRouter
from pydantic import BaseModel

from app.domain import events
from app.domain.models import Post
from app.presentation.schema import (
    UserRegisterRequest,
    UserDeletionRequest,
    PostCreationRequest,
    PostCreationResponse,
    UserPosts,
    NewPostRequest,
)
from app.services.messagebus import handle

router = APIRouter()


@router.post("/users")
async def signup(request: UserRegisterRequest):
    event = events.UserCreationRequested(
        id=request.id, name=request.name, password=request.password
    )
    [user_id] = await handle(event)
    get_user_event = events.UserInfoRequested(id=user_id)
    [new_user] = await handle(get_user_event)
    return new_user


@router.get("/users/{user_id}")
async def get_user_info(user_id: str):
    event = events.UserInfoRequested(id=user_id)
    [user_info] = await handle(event)
    return user_info


@router.delete("/users/{user_id}", status_code=http.HTTPStatus.NO_CONTENT)
async def delete_user(user_id: str, request: UserDeletionRequest):
    event = events.UserDeletionRequested(id=user_id, password=request.password)
    await handle(event)


@router.post("/posts", response_model=PostCreationResponse)
async def create_post(request: PostCreationRequest):
    event = events.PostCreated(
        title=request.title, content=request.content, user_id=request.user_id
    )  # TODO(humphrey): add user password
    [post_id] = await handle(event)
    find_post_event = events.PostViewRequested(id=post_id)
    [new_post] = await handle(find_post_event)
    return new_post


@router.get("/posts/{post_id}")
async def get_post(post_id: str):
    event = events.PostViewRequested(id=post_id)
    [post] = await handle(event)
    return post


@router.get("/posts")
async def get_post_by_user_id(user_id: str):
    event = events.UserPostViewRequested(id=user_id)
    [posts] = await handle(event)
    return UserPosts(items=posts)


@router.get("/posts")
async def get_all_posts():
    [posts] = await handle(events.AllPostViewRequested())
    return UserPosts(items=posts)


@router.post("/posts/{post_id}")
async def update_post(post_id: str, new_post: NewPostRequest):
    [updated_post] = await handle(
        events.PostUpdated(
            id=post_id,
            new_post=Post(
                id=post_id,
                title=new_post.title,
                content=new_post.content,
                author=new_post.user_id,
            ),
        )
    )
    return updated_post


class PostDeleteRequest(BaseModel):
    user_id: str
    user_password: str


@router.delete("/posts/{post_id}", status_code=http.HTTPStatus.NO_CONTENT)
async def delete_post(post_id: str, request: PostDeleteRequest):
    await handle(
        events.PostDeleted(id=post_id)
    )  # TODO(humphrey): add user password and id
