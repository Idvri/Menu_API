from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy import UUID, Integer, Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src import Dish, Menu, Submenu
from src.schemas import CreateMenuSchema
from src.utils.caching import delete_cache
from src.utils.universal import reverse


async def get_menus_db(session: AsyncSession) -> list[Row]:
    """Функция для получения списка меню."""

    m = aliased(Menu)
    s = aliased(Submenu)
    d = aliased(Dish)
    query = (
        select(
            m.id,
            m.title,
            m.description,
            func.count(s.id.distinct()).cast(Integer).label('submenus_count'),
            func.count(d.id.distinct()).cast(Integer).label('dishes_count')
        )
        .join(s, s.menu_id == m.id, isouter=True)
        .join(d, d.submenu_id == s.id, isouter=True)
        .group_by(m.id)
    )
    result = await session.execute(query)
    menus = result.unique().all()
    return menus


async def get_menu_db(menu_id: UUID, session: AsyncSession) -> Row:
    """Функция для получения меню."""

    m = aliased(Menu)
    s = aliased(Submenu)
    d = aliased(Dish)
    query = (
        select(
            m.id,
            m.title,
            m.description,
            func.count(s.id.distinct()).cast(Integer).label('submenus_count'),
            func.count(d.id.distinct()).cast(Integer).label('dishes_count')
        )
        .join(s, s.menu_id == m.id, isouter=True)
        .join(d, d.submenu_id == s.id, isouter=True)
        .where(m.id == menu_id)
        .group_by(m.id)
    )
    result = await session.execute(query)
    menu = result.unique().one_or_none()
    return menu


async def get_menu_db_for_update(target_menu_id: UUID, data: CreateMenuSchema, session: AsyncSession) -> Row:
    """Функция для обновления меню."""

    query = select(Menu).where(Menu.id == str(target_menu_id))
    result = await session.execute(query)
    menu = result.scalars().unique().one_or_none()
    if menu:
        menu.title = data.title
        menu.description = data.description
        await session.commit()
    return menu


async def get_menu_db_for_delete(target_menu_id: UUID, session: AsyncSession) -> Row:
    """Функция для удаления меню."""

    query = select(Menu).where(Menu.id == str(target_menu_id))
    result = await session.execute(query)
    menu = result.scalars().unique().one_or_none()
    if menu:
        await session.delete(menu)
        await session.commit()
    return menu


async def delete_depended_menu_cache(
        request: Request,
        target_menu_id: UUID,
        redis_client: Redis,
):
    """Функция для удаления кэша меню."""

    await delete_cache(
        key=await reverse('get_menu', request, target_menu_id=target_menu_id),
        redis_client=redis_client
    )
    await delete_cache(
        key=await reverse('get_menus', request),
        redis_client=redis_client
    )
