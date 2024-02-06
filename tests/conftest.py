from typing import AsyncGenerator

import pytest
from redis.asyncio import Redis
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src import (
    DB_HOST_TEST,
    DB_NAME_TEST,
    DB_PASS_TEST,
    DB_PORT_TEST,
    DB_USER_TEST,
    REDIS_HOST_TEST,
    REDIS_PORT_TEST,
    Base,
    get_async_redis_client,
    get_async_session,
)

DATABASE_URL_TEST = f'postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}'

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Функция получения сессии для обращения к тестовой БД."""

    async with async_session_maker() as session:
        yield session


async def override_get_async_redis_client() -> AsyncGenerator[Redis, None]:
    """Функция получения redis_client'а для работы с кэшом."""

    async with Redis(host=REDIS_HOST_TEST, port=int(REDIS_PORT_TEST)) as redis_client:
        yield redis_client


app.dependency_overrides[get_async_session] = override_get_async_session
app.dependency_overrides[get_async_redis_client] = override_get_async_redis_client


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    """Функция для создания записей тестовой БД и их удаления после тестирования."""

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        gen = get_async_redis_client(REDIS_HOST_TEST, REDIS_PORT_TEST)
        awaitable = anext(gen)
        redis_client = await awaitable
        await redis_client.flushdb()
        await conn.run_sync(Base.metadata.drop_all)
