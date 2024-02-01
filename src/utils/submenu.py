from fastapi import Depends
from sqlalchemy import UUID, Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src import Dish, Submenu, get_async_session
from src.utils.universal import check_db_obj


async def get_submenus_db(
        menu_id: UUID,
        session: AsyncSession = Depends(get_async_session)
) -> list[Submenu]:
    """Функция для получения списка подменю."""

    query = select(Submenu).where(Submenu.menu_id == menu_id)
    result = await session.execute(query)
    submenus = result.scalars().unique().all()
    return submenus


async def get_submenu_db(
        menu_id: UUID,
        submenu_id: UUID,
        session: AsyncSession = Depends(get_async_session)
) -> Submenu:
    """Функция для получения подменю."""

    query = select(Submenu).where(Submenu.menu_id == menu_id, Submenu.id == submenu_id)
    result = await session.execute(query)
    submenu = result.scalars().unique().one()
    check_db_obj(submenu, 'submenu')
    return submenu


async def get_submenu_db_with_counters(submenu_id: UUID, session: AsyncSession = Depends(get_async_session)) -> tuple:
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
