import json
from uuid import UUID

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from src import get_async_redis_client, get_async_session
from src.schemas import (
    CreateSubmenuSchema,
    MessageSchema,
    SubmenuSchema,
    SubmenuSchemaWithCounter,
)
from src.utils import (
    check_db_obj,
    create_db_obj,
    get_submenu_db,
    get_submenu_db_with_counters,
    get_submenus_db,
)

router = APIRouter(
    prefix='/submenus',
)


@router.get(
    '/',
    response_model=list[SubmenuSchema],
    status_code=HTTP_200_OK,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Submenu'],

)
async def get_submenus(
        target_menu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения подменю определенного меню."""

    cashed_submenus = await redis_client.get(f'{target_menu_id} submenus')
    if cashed_submenus:
        return json.loads(cashed_submenus)

    try:
        submenus = await get_submenus_db(target_menu_id, session)
    except NoResultFound as exc:
        exc.args = 'menu'
        raise exc
    return submenus


@router.post(
    '/',
    response_model=SubmenuSchema,
    status_code=HTTP_201_CREATED,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Submenu'],
)
async def create_submenu(
        target_menu_id: UUID,
        data: CreateSubmenuSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для создания подменю."""

    try:
        submenu = await create_db_obj(target_menu_id, data, session)
    except IntegrityError:
        return JSONResponse(content={'detail': 'menu not found'}, status_code=HTTP_404_NOT_FOUND)

    cashed_submenus = await redis_client.get(f'{target_menu_id} submenus')
    if not cashed_submenus:
        submenus = []
    else:
        submenus = json.loads(cashed_submenus)
    submenu_for_cache = {
        'id': str(submenu.id),
        'title': submenu.title,
        'description': submenu.description,
    }
    submenus.append(submenu_for_cache)
    await redis_client.set(name=f'{target_menu_id} submenus', value=json.dumps(submenus), ex=300)

    cached_menu = json.loads(str(await redis_client.get(str(target_menu_id))))
    cached_menu['submenus_count'] += 1
    await redis_client.set(name=cached_menu['id'], value=json.dumps(cached_menu), ex=300)

    submenu_for_cache = {
        'id': str(submenu.id),
        'title': submenu.title,
        'description': submenu.description,
        'dishes_count': 0,
    }
    await redis_client.set(name=submenu_for_cache['id'], value=json.dumps(submenu_for_cache), ex=300)

    return submenu


@router.get(
    '/{target_submenu_id}',
    response_model=SubmenuSchemaWithCounter,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Submenu'],
)
async def get_submenu(
        target_submenu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения подменю."""

    cache_value = await redis_client.get(str(target_submenu_id))
    if cache_value:
        return json.loads(cache_value)

    submenu = await get_submenu_db_with_counters(target_submenu_id, session)
    check_db_obj(submenu, 'submenu')
    return submenu


@router.patch(
    '/{target_submenu_id}',
    response_model=SubmenuSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Submenu'],
)
async def update_submenu(
        target_submenu_id: UUID,
        data: CreateSubmenuSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для изменения подменю."""

    submenu = await get_submenu_db(target_submenu_id, session)
    check_db_obj(submenu, 'submenu')
    submenu.title = data.title
    submenu.description = data.description
    await session.commit()

    cache_value = await redis_client.get(str(target_submenu_id))
    if cache_value:
        cache_to_change = json.loads(cache_value)
        cache_to_change['title'] = submenu.title
        cache_to_change['description'] = submenu.description
        await redis_client.set(name=cache_to_change['id'], value=json.dumps(cache_to_change), ex=300)

    return submenu


@router.delete(
    '/{target_submenu_id}',
    responses={
        HTTP_200_OK: {'model': MessageSchema},
        HTTP_404_NOT_FOUND: {'model': MessageSchema},
    },
    tags=['Submenu'],
)
async def delete_submenu(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для удаления подменю."""

    submenu = await get_submenu_db(target_submenu_id, session)
    check_db_obj(submenu, 'submenu')
    for dish in submenu.dishes:
        await session.delete(dish)
    await session.delete(submenu)
    await session.commit()

    cashed_dishes_count = json.loads(str(await redis_client.get(str(submenu.id))))['dishes_count']

    await redis_client.delete(str(submenu.id))
    cashed_submenus = json.loads(str(await redis_client.get(f'{target_menu_id} submenus')))
    item = [item for item in cashed_submenus if item['id'] == str(submenu.id)]
    cashed_submenus.remove(item[0])
    await redis_client.set(name=f'{target_menu_id} submenus', value=json.dumps(cashed_submenus), ex=300)

    cached_menu = json.loads(str(await redis_client.get(str(target_menu_id))))
    cached_menu['submenus_count'] -= 1
    cached_menu['dishes_count'] -= cashed_dishes_count
    await redis_client.set(name=cached_menu['id'], value=json.dumps(cached_menu), ex=300)

    cached_dishes = await redis_client.get(f'{target_submenu_id} dishes')
    if cached_dishes:
        cached_dishes = json.loads(cached_dishes)
        for cached_dish in cached_dishes:
            await redis_client.delete(cached_dish['id'])
        await redis_client.delete(f'{target_submenu_id} dishes')
    await redis_client.delete(f'{submenu.id} dishes')

    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
