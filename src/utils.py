from fastapi import Depends

from sqlalchemy import UUID, select, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src import Menu, Submenu, get_async_session, Dish


async def get_menu_db(menu_id: UUID, session: AsyncSession = Depends(get_async_session)) -> tuple:
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
    data = result.unique().one_or_none()
    return data


async def get_submenu_db(submenu_id: UUID, session: AsyncSession = Depends(get_async_session)) -> tuple:
    """Функция для получения подменю с выводом кол-ва блюд."""

    s = aliased(Submenu)
    d = aliased(Dish)
    query = (
        select(
            s.id,
            s.title,
            s.description,
            func.count(d.id).cast(Integer).label('dishes_count')
        )
        .join(d, d.submenu_id == s.id, isouter=True)
        .where(s.id == submenu_id)
        .group_by(s.id)
    )
    result = await session.execute(query)
    data = result.unique().one_or_none()
    return data
