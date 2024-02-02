from fastapi import Depends
from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import Dish, get_async_session


async def get_dishes_db(submenu_id: UUID, session: AsyncSession = Depends(get_async_session)) -> list[Dish]:
    """Функция для получения списка блюд."""

    query = select(Dish).where(Dish.submenu_id == submenu_id)
    result = await session.execute(query)
    dishes = result.scalars().unique().all()
    return dishes


async def get_dish_db(dish_id: UUID, session: AsyncSession = Depends(get_async_session)) -> Dish:
    """Функция для получения блюда."""

    query = select(Dish).where(Dish.id == dish_id)
    result = await session.execute(query)
    dish = result.scalars().unique().one_or_none()
    return dish
