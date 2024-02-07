from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy import UUID, Integer, Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src import Dish, Submenu, get_async_session
from src.schemas import CreateSubmenuSchema
from src.utils.caching import delete_cache
from src.utils.universal import reverse


async def get_submenus_db(
        menu_id: UUID,
        session: AsyncSession = Depends(get_async_session)
) -> list[Row]:
    """Функция для получения списка подменю."""

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
        .where(s.menu_id == menu_id)
        .group_by(s.id)
    )
    result = await session.execute(query)
    data = result.unique().all()
    return data


async def get_submenu_db(
        menu_id: UUID,
        submenu_id: UUID,
        session: AsyncSession = Depends(get_async_session)
) -> Row:
    """Функция для получения подменю."""

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
        .where(s.id == submenu_id, s.menu_id == menu_id)
        .group_by(s.id)
    )
    result = await session.execute(query)
    data = result.unique().one_or_none()
    return data


async def get_submenu_db_for_update(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        data: CreateSubmenuSchema,
        session: AsyncSession
) -> Row:
    """Функция для обновления подменю."""

    query = select(Submenu).where(Submenu.id == str(target_submenu_id), Submenu.menu_id == str(target_menu_id))
    result = await session.execute(query)
    submenu = result.scalars().unique().one_or_none()
    if submenu:
        submenu.title = data.title
        submenu.description = data.description
        await session.commit()
    return submenu


async def get_submenu_db_for_delete(target_menu_id: UUID, target_submenu_id: UUID, session: AsyncSession) -> Row:
    """Функция для удаления подменю."""

    query = select(Submenu).where(Submenu.id == str(target_submenu_id), Submenu.menu_id == str(target_menu_id))
    result = await session.execute(query)
    submenu = result.scalars().unique().one_or_none()
    if submenu:
        await session.delete(submenu)
        await session.commit()
    return submenu


async def delete_depended_submenu_cache(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        redis_client: Redis,
):
    """Функция для удаления кэша подменю."""

    await delete_cache(
        key=await reverse('get_submenu', request, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id),
        redis_client=redis_client
    )
    await delete_cache(
        key=await reverse('get_submenus', request, target_menu_id=target_menu_id),
        redis_client=redis_client
    )
