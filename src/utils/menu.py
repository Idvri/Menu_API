from fastapi import Depends
from sqlalchemy import UUID, Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src import Dish, Menu, Submenu, get_async_session


async def get_menus_db(
        session: AsyncSession = Depends(get_async_session)
) -> list[Menu]:
    """Функция для получения списка меню."""

    query = select(Menu)
    result = await session.execute(query)
    menus = result.scalars().unique().all()
    return menus


async def get_menu_db(target_id: UUID, session: AsyncSession = Depends(get_async_session)) -> Menu:
    """Функция для получения меню."""

    query = select(Menu).where(Menu.id == target_id)
    result = await session.execute(query)
    menu = result.scalars().unique().one_or_none()
    return menu


async def get_menu_db_with_counters(menu_id: UUID, session: AsyncSession = Depends(get_async_session)) -> tuple:
    """Функция для получения меню с выводом кол-ва подменю и блюд."""

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
