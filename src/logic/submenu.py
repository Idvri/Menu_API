from uuid import UUID

from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from src.schemas import CreateSubmenuSchema, SubmenuSchema
from src.utils import (
    CacheNotFound,
    check_db_obj,
    create_db_obj,
    delete_all_depended_cache,
    delete_cache,
    delete_depended_menu_cache,
    delete_depended_submenu_cache,
    get_cache,
    get_menu_db,
    get_submenu_db,
    get_submenu_db_for_delete,
    get_submenu_db_for_update,
    get_submenus_db,
    reverse,
    set_cache,
)


async def get_submenus_logic(
        request: Request,
        target_menu_id: UUID,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику получения списка подменю."""

    path = await reverse('get_submenus', request, target_menu_id=target_menu_id)
    try:
        cache = await get_cache(
            key=path,
            redis_client=redis_client,
        )
    except CacheNotFound:
        menu = await get_menu_db(target_menu_id, session)
        await check_db_obj(menu, 'menu')
        data = await get_submenus_db(target_menu_id, session)
        await set_cache(
            key=path,
            value=[SubmenuSchema(**submenu._asdict()).model_dump() for submenu in data],
            redis_client=redis_client,
        )
        return data
    else:
        return cache


async def create_submenu_logic(
        request: Request,
        target_menu_id: UUID,
        data: CreateSubmenuSchema,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для создания подменю."""

    path = await reverse('get_submenus', request, target_menu_id=target_menu_id)
    try:
        submenu = await create_db_obj(obj_id=target_menu_id, data=data, session=session)
        await delete_cache(key=path, redis_client=redis_client)
        await delete_depended_menu_cache(request, target_menu_id, redis_client)
    except IntegrityError:
        return JSONResponse(content={'detail': 'menu not found'}, status_code=HTTP_404_NOT_FOUND)
    return submenu


async def get_submenu_logic(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для получения определенного подменю."""

    path = await reverse('get_submenu', request, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id)
    try:
        cache = await get_cache(
            key=path,
            redis_client=redis_client,
        )
        await get_cache(
            key=await reverse('get_submenus', request, target_menu_id=target_menu_id),
            redis_client=redis_client,
        )
    except CacheNotFound:
        data = await get_submenu_db(target_menu_id, target_submenu_id, session)
        await check_db_obj(data, 'submenu')
        await set_cache(
            key=path,
            value=SubmenuSchema(**data._asdict()).model_dump(),
            redis_client=redis_client,
        )
        return data
    else:
        return cache


async def update_submenu_logic(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        data: CreateSubmenuSchema,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для изменения определенного подменю."""

    submenu = await get_submenu_db_for_update(target_menu_id, target_submenu_id, data, session)
    await check_db_obj(submenu, 'submenu')
    updated_submenu = await get_submenu_db(target_menu_id, target_submenu_id, session)
    await delete_depended_submenu_cache(request, target_menu_id, target_submenu_id, redis_client)
    return updated_submenu


async def delete_submenu_logic(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для удаления определенного подменю."""

    submenu = await get_submenu_db_for_delete(target_menu_id, target_submenu_id, session)
    await check_db_obj(submenu, 'submenu')
    try:
        await delete_all_depended_cache(request, target_menu_id, redis_client)
    except CacheNotFound:
        await delete_depended_submenu_cache(request, target_menu_id, target_submenu_id, redis_client)
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
