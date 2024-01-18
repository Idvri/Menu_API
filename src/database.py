from src import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from typing import AsyncGenerator, Annotated

from sqlalchemy import Integer
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

INT_PK = Annotated[
    int,
    mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
]

Base: DeclarativeMeta = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Функция получения сессии для обращения к БД."""
    async with async_session_maker() as session:
        yield session
