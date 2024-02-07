from uuid import UUID

from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from src import get_async_redis_client, get_async_session
from src.logic import (
    create_dish_logic,
    delete_dish_logic,
    get_dish_logic,
    get_dishes_logic,
    update_dish_logic,
)
from src.schemas import CreateDishSchema, DishSchema, MessageSchema

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
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения блюд."""

    return await get_dishes_logic(request, target_menu_id, target_submenu_id, session, redis_client)


@router.post(
    '/',
    response_model=DishSchema,
    status_code=HTTP_201_CREATED,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Dish'],
)
async def create_dish(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        data: CreateDishSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для создания блюда."""

    return await create_dish_logic(request, target_menu_id, target_submenu_id, data, session, redis_client)


@router.get(
    '/{target_dish_id}',
    response_model=DishSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Dish'],
)
async def get_dish(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения блюда."""

    return await get_dish_logic(
        request,
        target_menu_id,
        target_submenu_id,
        target_dish_id,
        session,
        redis_client
    )


@router.patch(
    '/{target_dish_id}',
    response_model=DishSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Dish'],
)
async def update_dish(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        data: CreateDishSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для изменения блюда."""

    return await update_dish_logic(
        request,
        target_menu_id,
        target_submenu_id,
        target_dish_id,
        data,
        session,
        redis_client
    )


@router.delete(
    '/{target_dish_id}',
    responses={
        HTTP_200_OK: {'model': MessageSchema},
        HTTP_404_NOT_FOUND: {'model': MessageSchema},
    },
    tags=['Dish'],
)
async def delete_dish(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        target_dish_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для удаления блюда."""

    return await delete_dish_logic(
        request,
        target_menu_id,
        target_submenu_id,
        target_dish_id,
        session,
        redis_client
    )
