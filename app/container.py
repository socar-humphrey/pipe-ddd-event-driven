import databases
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration
from pydantic import BaseSettings, Field

from app.services.uow import AsyncORMUnitOfWork


class DatabaseConfig(BaseSettings):
    url: str = Field(default="sqlite:///./test.db", env="db_url")


class AppConfig(BaseSettings):
    db = DatabaseConfig()


class Container(DeclarativeContainer):
    config = Configuration()
    database = providers.Singleton(databases.Database, config.db.url)
    uow = providers.Singleton(AsyncORMUnitOfWork, database=database)