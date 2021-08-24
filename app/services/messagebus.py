from dependency_injector.wiring import inject, Provide

import app.domain.events
from app.container import Container
from app.domain import events
from app.services import usecases
from app.services.uow import UnitOfWork


@inject
async def handle(
    event: app.domain.events.Event, uow: UnitOfWork = Provide[Container.uow]
):  # TODO(humphrey): add container
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(await handler(event, uow=uow))
    return results


HANDLERS = {
    events.UserCreationRequested: [usecases.create_user],
    events.UserInfoRequested: [usecases.get_user],
    events.UserDeletionRequested: [usecases.delete_user],
    events.UserPostViewRequested: [usecases.get_post_by_user],
    events.AllPostViewRequested: [usecases.get_all_posts],
    events.PostCreated: [usecases.create_post],
    events.PostDeleted: [usecases.delete_post],
    events.PostUpdated: [usecases.update_post],
}
