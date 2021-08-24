from app.domain.models import User, Post
from app.domains.events import UserCreationRequested, UserInfoRequested, UserDeletionRequested, PostCreated, \
    PostViewRequested, UserPostViewRequested, AllPostViewRequested, PostUpdated, PostDeleted
from app.services.uow import UnitOfWork


async def create_user(event: UserCreationRequested, uow: UnitOfWork):
    async with uow:
        await uow.users.add(
            User(id=event.id, name=event.name, password=event.password)
        )
        await uow.commit()
    return event.id


async def get_user(event: UserInfoRequested, uow: UnitOfWork):
    async with uow:
        return await uow.users.get_by_id(_id=event.id)


async def delete_user(event: UserDeletionRequested, uow: UnitOfWork):
    async with uow:
        await uow.users.delete(_id=event.id)  # todo(humphrey): add password to repository
        await uow.commit()


async def create_post(event: PostCreated, uow: UnitOfWork):
    async with uow:
        author = await uow.users.get_by_id(event.user_id)
        await uow.posts.add(
            Post(id=event.id, title=event.title, content=event.content, author=author)
        )
        await uow.commit()
    return event.id


async def get_post(event: PostViewRequested, uow: UnitOfWork):
    async with uow:
        return await uow.posts.get_by_id(_id=event.id)


async def get_post_by_user(event: UserPostViewRequested, uow: UnitOfWork):
    async with uow:
        return await uow.users.get_user_posts(_id=event.id)


async def get_all_posts(event: AllPostViewRequested, uow: UnitOfWork):
    async with uow:
        return await uow.posts.get_all()


async def update_post(event: PostUpdated, uow: UnitOfWork):
    async with uow:
        await uow.posts.update(event.id, event.new_post)
    return event.id


async def delete_post(event: PostDeleted, uow: UnitOfWork):
    async with uow:
        await uow.posts.delete(_id=event.id)
