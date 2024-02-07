from uuid import UUID

from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from src.schemas import CreateDishSchema, DishSchema
from src.utils import (
    CacheNotFound,
    check_db_obj,
    create_db_obj,
    delete_all_depended_cache,
    delete_cache,
    delete_depended_dish_cache,
    delete_depended_menu_cache,
    delete_depended_submenu_cache,
    get_cache,
    get_dish_db,
    get_dish_db_for_delete,
    get_dish_db_for_update,
    get_dishes_db,
    get_menu_db,
    get_submenu_db,
    reverse,
    set_cache,
)


async def get_dishes_logic(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику получения списка блюд."""

    path = await reverse('get_dishes', request, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id)
    try:
        cache = await get_cache(
            key=path,
            redis_client=redis_client,
        )
    except CacheNotFound:
        menu = await get_menu_db(target_menu_id, session)
        await check_db_obj(menu, 'menu')
        submenu = await get_submenu_db(target_menu_id, target_submenu_id, session)
        await check_db_obj(submenu, 'submenu')
        data = await get_dishes_db(target_menu_id, target_submenu_id, session)
        await set_cache(
            key=path,
            value=[DishSchema(**dish._asdict()).model_dump() for dish in data],
            redis_client=redis_client,
        )
        return data
    else:
        return cache


async def create_dish_logic(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        data: CreateDishSchema,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для создания блюда."""

    path = await reverse('get_dishes', request, target_menu_id=target_menu_id, target_submenu_id=target_submenu_id)
    try:
        dish = await create_db_obj(obj_id=target_submenu_id, data=data, session=session)
        await delete_cache(key=path, redis_client=redis_client)
        await delete_depended_menu_cache(request, target_menu_id, redis_client)
        await delete_depended_submenu_cache(request, target_menu_id, target_submenu_id, redis_client)
    except IntegrityError:
        return JSONResponse(content={'detail': 'submenu not found'}, status_code=HTTP_404_NOT_FOUND)
    return dish


async def get_dish_logic(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для получения определенного блюда."""

    path = await reverse(
        'get_dish',
        request,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        target_dish_id=target_dish_id
    )
    try:
        cache = await get_cache(
            key=path,
            redis_client=redis_client,
        )
        await get_cache(
            key=await reverse(
                'get_dishes',
                request,
                target_menu_id=target_menu_id,
                target_submenu_id=target_submenu_id
            ),
            redis_client=redis_client,
        )
    except CacheNotFound:
        data = await get_dish_db(target_menu_id, target_submenu_id, target_dish_id, session)
        await check_db_obj(data, 'dish')
        await set_cache(
            key=path,
            value=DishSchema(**data._asdict()).model_dump(),
            redis_client=redis_client,
        )
        return data
    else:
        return cache


async def update_dish_logic(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        data: CreateDishSchema,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для изменения определенного блюда."""

    dish = await get_dish_db_for_update(target_menu_id, target_submenu_id, target_dish_id, data, session)
    await check_db_obj(dish, 'dish')
    updated_dish = await get_dish_db(target_menu_id, target_submenu_id, target_dish_id, session)
    await delete_depended_dish_cache(request, target_menu_id, target_submenu_id, target_dish_id, redis_client)
    return updated_dish


async def delete_dish_logic(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        session: AsyncSession,
        redis_client: Redis,
):
    """Функция описывающая логику для удаления определенного блюда."""

    dish = await get_dish_db_for_delete(target_menu_id, target_submenu_id, target_dish_id, session)
    await check_db_obj(dish, 'dish')
    try:
        await delete_all_depended_cache(request, target_menu_id, redis_client)
    except CacheNotFound:
        await delete_depended_submenu_cache(request, target_menu_id, target_submenu_id, redis_client)
        await delete_depended_dish_cache(request, target_menu_id, target_submenu_id, target_dish_id, redis_client)
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
