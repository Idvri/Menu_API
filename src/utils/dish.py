from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy import UUID, Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import Dish, Submenu

from ..schemas import CreateDishSchema
from .caching import delete_cache
from .universal import reverse


async def get_dishes_db(
        menu_id: UUID, submenu_id: UUID, session: AsyncSession
) -> list[Row]:
    """Функция для получения списка блюд."""

    query = (
        select(
            Dish.id,
            Dish.title,
            Dish.description,
            Dish.price
        ).join(
            Submenu,
            Submenu.menu_id == menu_id,
            isouter=True
        ).where(
            Dish.submenu_id == submenu_id
        )
        .group_by(Dish.id)
    )
    result = await session.execute(query)
    dishes = result.unique().all()
    return dishes


async def get_dish_db(
        menu_id: UUID, submenu_id: UUID, dish_id: UUID, session: AsyncSession
) -> Row:
    """Функция для получения блюда."""

    query = (
        select(
            Dish.id,
            Dish.title,
            Dish.description,
            Dish.price
        ).join(
            Submenu,
            Submenu.menu_id == menu_id,
            isouter=True
        ).where(
            Dish.id == dish_id,
            Dish.submenu_id == submenu_id
        )
        .group_by(Dish.id)
    )
    result = await session.execute(query)
    dish = result.unique().one_or_none()
    return dish


async def get_dish_db_for_update(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        data: CreateDishSchema,
        session: AsyncSession
) -> Dish:
    """Функция для обновления блюда."""

    query = (
        select(
            Dish
        ).join(
            Submenu,
            Submenu.menu_id == target_menu_id,
            isouter=True
        ).where(
            Dish.id == target_dish_id,
            Dish.submenu_id == target_submenu_id
        )
        .group_by(Dish.id)
    )
    result = await session.execute(query)
    dish = result.scalars().unique().one_or_none()
    if dish:
        dish.title = data.title
        dish.description = data.description
        dish.price = data.price
        await session.commit()
    return dish


async def get_dish_db_for_delete(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        session: AsyncSession
) -> Dish:
    """Функция для удаления блюда."""

    query = (
        select(
            Dish
        ).join(
            Submenu,
            Submenu.menu_id == target_menu_id,
            isouter=True
        ).where(
            Dish.id == target_dish_id,
            Dish.submenu_id == target_submenu_id
        )
        .group_by(Dish.id)
    )
    result = await session.execute(query)
    dish = result.scalars().unique().one_or_none()
    if dish:
        await session.delete(dish)
        await session.commit()
    return dish


async def delete_depended_dish_cache(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        redis_client: Redis,
) -> None:
    """Функция для удаления кэша блюда."""

    await delete_cache(
        key=await reverse(
            'get_dish',
            request,
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id,
        ),
        redis_client=redis_client
    )
    await delete_cache(
        key=await reverse('get_dishes', request, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id),
        redis_client=redis_client
    )
