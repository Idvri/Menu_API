from uuid import UUID

from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK

from src.schemas import CreateMenuSchema, MenuSchema
from src.utils import (
    CacheNotFound,
    check_db_obj,
    create_db_obj,
    delete_all_depended_cache,
    delete_cache,
    delete_depended_menu_cache,
    get_cache,
    get_menu_db,
    get_menu_db_for_delete,
    get_menu_db_for_update,
    get_menus_db,
    reverse,
    set_cache,
)


async def get_menus_logic(
        request: Request,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику получения списка меню"""

    try:
        cache = await get_cache(
            key=await reverse('get_menus', request),
            redis_client=redis_client,
        )
    except CacheNotFound:
        data = await get_menus_db(session)
        await set_cache(
            key=await reverse('get_menus', request),
            value=[MenuSchema(**menu._asdict()).model_dump() for menu in data],
            redis_client=redis_client,
        )
        return data
    else:
        return cache


async def create_menu_logic(
        request: Request,
        data: CreateMenuSchema,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для создания меню."""

    menu = await create_db_obj(data=data, session=session)
    await delete_cache(key=await reverse('get_menus', request), redis_client=redis_client)
    return menu


async def get_menu_logic(
        request: Request,
        target_menu_id: UUID,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для получения определенного меню."""

    try:
        cache = await get_cache(
            key=await reverse('get_menu', request, target_menu_id=target_menu_id),
            redis_client=redis_client,
        )
        await get_cache(
            key=await reverse('get_menus', request),
            redis_client=redis_client,
        )
    except CacheNotFound:
        data = await get_menu_db(target_menu_id, session)
        await check_db_obj(data, 'menu')
        await set_cache(
            key=await reverse('get_menu', request, target_menu_id=target_menu_id),
            value=MenuSchema(**data._asdict()).model_dump(),
            redis_client=redis_client,
        )
        return data
    else:
        return cache


async def update_menu_logic(
        request: Request,
        target_menu_id: UUID,
        data: CreateMenuSchema,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для изменения определенного меню."""

    menu = await get_menu_db_for_update(target_menu_id, data, session)
    await check_db_obj(menu, 'menu')
    updated_menu = await get_menu_db(target_menu_id, session)
    await delete_depended_menu_cache(request, target_menu_id, redis_client)
    return updated_menu


async def delete_menu_logic(
        request: Request,
        target_menu_id: UUID,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для удаления определенного меню."""

    menu = await get_menu_db_for_delete(target_menu_id, session)
    await check_db_obj(menu, 'menu')
    try:
        await delete_all_depended_cache(request, target_menu_id, redis_client)
    except CacheNotFound:
        pass
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
