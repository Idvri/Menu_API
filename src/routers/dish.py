import json
from uuid import UUID

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from src import get_async_redis_client, get_async_session
from src.schemas import CreateDishSchema, DishSchema, MessageSchema
from src.utils import check_db_obj, create_db_obj, get_dish_db, get_dishes_db

router = APIRouter(
    prefix='/dishes',
)


@router.get(
    '/',
    response_model=list[DishSchema],
    status_code=HTTP_200_OK,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Dish'],
)
async def get_dishes(
        target_submenu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения блюд."""

    cashed_dishes = await redis_client.get(f'{target_submenu_id} dishes')
    if cashed_dishes:
        return json.loads(cashed_dishes)

    try:
        dishes = await get_dishes_db(target_submenu_id, session)
    except NoResultFound:
        return JSONResponse(content=[], status_code=HTTP_200_OK)
    return dishes


@router.post(
    '/',
    response_model=DishSchema,
    status_code=HTTP_201_CREATED,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Dish'],
)
async def create_dish(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        data: CreateDishSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для создания блюда."""

    try:
        dish = await create_db_obj(target_submenu_id, data, session)
    except IntegrityError:
        return JSONResponse(content={'detail': 'submenu not found'}, status_code=HTTP_404_NOT_FOUND)

    cashed_dishes = await redis_client.get(f'{target_submenu_id} dishes')
    if not cashed_dishes:
        dishes = []
    else:
        dishes = json.loads(cashed_dishes)
    dish_for_cache = {
        'id': str(dish.id),
        'title': dish.title,
        'description': dish.description,
        'price': dish.price,
    }
    dishes.append(dish_for_cache)
    await redis_client.set(name=f'{target_submenu_id} dishes', value=json.dumps(dishes), ex=300)

    dish_for_cache = {
        'id': str(dish.id),
        'title': dish.title,
        'description': dish.description,
        'price': dish.price,
    }
    await redis_client.set(name=dish_for_cache['id'], value=json.dumps(dish_for_cache), ex=300)

    cached_menu = await redis_client.get(str(target_menu_id))
    if cached_menu:
        cached_menu = json.loads(cached_menu)
        cached_menu['dishes_count'] += 1
        await redis_client.set(name=cached_menu['id'], value=json.dumps(cached_menu), ex=300)

    cached_submenu = await redis_client.get(str(target_submenu_id))
    if cached_submenu:
        cached_submenu = json.loads(cached_submenu)
        cached_submenu['dishes_count'] += 1
        await redis_client.set(name=cached_submenu['id'], value=json.dumps(cached_submenu), ex=300)

    return dish


@router.get(
    '/{target_dish_id}',
    response_model=DishSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Dish'],
)
async def get_dish(
        target_dish_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения блюда."""

    cache_value = await redis_client.get(str(target_dish_id))
    if cache_value:
        return json.loads(cache_value)

    dish = await get_dish_db(target_dish_id, session)
    check_db_obj(dish, 'dish')

    return dish


@router.patch(
    '/{target_dish_id}',
    response_model=DishSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Dish'],
)
async def update_dish(
        target_submenu_id: UUID,
        target_dish_id: UUID,
        data: CreateDishSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для изменения блюда."""

    dish = await get_dish_db(target_dish_id, session)
    check_db_obj(dish, 'dish')
    dish.title = data.title
    dish.description = data.description
    dish.price = data.price
    await session.commit()

    cache_value = await redis_client.get(str(target_dish_id))
    if cache_value:
        cache_to_change = json.loads(cache_value)
        cache_to_change['title'] = dish.title
        cache_to_change['description'] = dish.description
        cache_to_change['price'] = dish.price
        await redis_client.set(name=cache_to_change['id'], value=json.dumps(cache_to_change), ex=300)

    cashed_dishes = await redis_client.get(f'{target_submenu_id} dishes')
    if not cashed_dishes:
        dishes = []
    else:
        dishes = json.loads(cashed_dishes)
    dish_for_cache = {
        'id': str(dish.id),
        'title': dish.title,
        'description': dish.description,
        'price': dish.price,
    }
    for dish_from_cache in dishes:
        if dish_from_cache['id'] == str(dish.id):
            dishes.remove(dish_from_cache)
    dishes.append(dish_for_cache)
    await redis_client.set(name=f'{target_submenu_id} dishes', value=json.dumps(dishes), ex=300)

    return dish


@router.delete(
    '/{target_dish_id}',
    responses={
        HTTP_200_OK: {'model': MessageSchema},
        HTTP_404_NOT_FOUND: {'model': MessageSchema},
    },
    tags=['Dish'],
)
async def delete_dish(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для удаления блюда."""

    dish = await get_dish_db(target_dish_id, session)
    check_db_obj(dish, 'dish')
    await session.delete(dish)
    await session.commit()

    await redis_client.delete(str(dish.id))
    cashed_dishes = await redis_client.get(f'{target_submenu_id} dishes')
    if cashed_dishes:
        cashed_dishes = json.loads(cashed_dishes)
        item = [item for item in cashed_dishes if item['id'] == str(dish.id)]
        cashed_dishes.remove(item[0])
        await redis_client.set(name=f'{target_submenu_id} dishes', value=json.dumps(cashed_dishes), ex=300)

    cached_menu = await redis_client.get(str(target_menu_id))
    if cached_menu:
        cached_menu = json.loads(cached_menu)
        cached_menu['dishes_count'] -= 1
        await redis_client.set(name=cached_menu['id'], value=json.dumps(cached_menu), ex=300)

    cached_submenu = await redis_client.get(str(target_submenu_id))
    if cached_submenu:
        cached_submenu = json.loads(cached_submenu)
        cached_submenu['dishes_count'] -= 1
        await redis_client.set(name=cached_submenu['id'], value=json.dumps(cached_submenu), ex=300)

    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
