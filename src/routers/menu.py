import json
from uuid import UUID

from fastapi import APIRouter, Depends
from redis.asyncio import Redis  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from src import get_async_redis_client, get_async_session
from src.schemas import (
    CreateMenuSchema,
    MenuSchema,
    MenuSchemaWithCounters,
    MessageSchema,
)
from src.utils import (
    check_db_obj,
    create_db_obj,
    get_menu_db,
    get_menu_db_with_counters,
    get_menus_db,
)

router = APIRouter(
    prefix='/menus',
)


@router.get(
    '/',
    response_model=list[MenuSchema],
    tags=['Menu'],
)
async def get_menus(
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения всех меню."""

    cashed_menus = await redis_client.get('menus')
    if cashed_menus:
        return json.loads(cashed_menus)

    menus = await get_menus_db(session)
    return menus


@router.post(
    '/',
    response_model=MenuSchema,
    status_code=HTTP_201_CREATED,
    tags=['Menu'],
)
async def create_menu(
        data: CreateMenuSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),

):
    """Эндпойнт для создания меню."""

    menu = await create_db_obj(data=data, session=session)

    cashed_menus = await redis_client.get('menus')
    if not cashed_menus:
        menus = []
    else:
        menus = json.loads(cashed_menus)
    menu_for_cache = {
        'id': str(menu.id),
        'title': menu.title,
        'description': menu.description,
    }
    menus.append(menu_for_cache)
    await redis_client.set(name='menus', value=json.dumps(menus), ex=300)

    return menu


@router.get(
    '/{target_menu_id}',
    response_model=MenuSchemaWithCounters,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Menu'],
)
async def get_menu(
        target_menu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения определенного меню."""

    cache_value = await redis_client.get(str(target_menu_id))
    if cache_value:
        return json.loads(cache_value)

    menu = await get_menu_db_with_counters(target_menu_id, session)
    check_db_obj(menu, 'menu')

    menu_for_cache = {
        'id': str(menu[0]),
        'title': menu[1],
        'description': menu[2],
        'submenus_count': menu[3],
        'dishes_count': menu[4],
    }
    await redis_client.set(name=menu_for_cache['id'], value=json.dumps(menu_for_cache), ex=300)

    return menu


@router.patch(
    '/{target_menu_id}',
    response_model=MenuSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Menu'],
)
async def update_menu(
        target_menu_id: UUID,
        data: CreateMenuSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для изменения определенного меню."""

    menu = await get_menu_db(target_menu_id, session)
    check_db_obj(menu, 'menu')
    menu.title = data.title
    menu.description = data.description
    await session.commit()

    cache_value = await redis_client.get(str(target_menu_id))
    if cache_value:
        cache_to_change = json.loads(cache_value)
        cache_to_change['title'] = menu.title
        cache_to_change['description'] = menu.description
        await redis_client.set(name=cache_to_change['id'], value=json.dumps(cache_to_change), ex=300)

    return menu


@router.delete(
    '/{target_menu_id}',
    responses={
        HTTP_200_OK: {'model': MessageSchema},
        HTTP_404_NOT_FOUND: {'model': MessageSchema},
    },
    tags=['Menu'],
)
async def delete_menu(
        target_menu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для удаления определенного меню."""

    menu = await get_menu_db(target_menu_id, session)
    check_db_obj(menu, 'menu')
    await session.delete(menu)
    await session.commit()

    await redis_client.delete(str(menu.id))
    cashed_menus = json.loads(await redis_client.get('menus'))
    item = [item for item in cashed_menus if item['id'] == str(menu.id)]
    cashed_menus.remove(item[0])
    await redis_client.set(name='menus', value=json.dumps(cashed_menus), ex=300)

    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
