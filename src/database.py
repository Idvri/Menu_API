from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import declarative_base

from src import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, REDIS_HOST, REDIS_PORT

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

Base: DeclarativeMeta = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Функция получения сессии для обращения к БД."""

    async with async_session_maker() as session:
        yield session


async def get_async_redis_client() -> AsyncGenerator[Redis, None]:
    """Функция получения redis_client'а для работы с кэшом."""

    async with Redis(host=REDIS_HOST, port=int(REDIS_PORT)) as redis_client:
        yield redis_client
