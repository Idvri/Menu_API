from uuid import UUID

from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from src import get_async_redis_client, get_async_session
from src.logic import (
    create_menu_logic,
    delete_menu_logic,
    get_menu_logic,
    get_menus_logic,
    update_menu_logic,
)
from src.schemas import CreateMenuSchema, MenuSchema, MessageSchema

router = APIRouter(
    prefix='/menus',
)


@router.get(
    '/',
    response_model=list[MenuSchema],
    tags=['Menu'],
)
async def get_menus(
        request: Request,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения всех меню."""

    return await get_menus_logic(request, session, redis_client)


@router.post(
    '/',
    response_model=MenuSchema,
    status_code=HTTP_201_CREATED,
    tags=['Menu'],
)
async def create_menu(
        request: Request,
        data: CreateMenuSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для создания меню."""

    return await create_menu_logic(request, data, session, redis_client)


@router.get(
    '/{target_menu_id}',
    response_model=MenuSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Menu'],
)
async def get_menu(
        request: Request,
        target_menu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения определенного меню."""

    return await get_menu_logic(request, target_menu_id, session, redis_client)


@router.patch(
    '/{target_menu_id}',
    response_model=MenuSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Menu'],
)
async def update_menu(
        request: Request,
        target_menu_id: UUID,
        data: CreateMenuSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для изменения определенного меню."""

    return await update_menu_logic(request, target_menu_id, data, session, redis_client)


@router.delete(
    '/{target_menu_id}',
    responses={
        HTTP_200_OK: {'model': MessageSchema},
        HTTP_404_NOT_FOUND: {'model': MessageSchema},
    },
    tags=['Menu'],
)
async def delete_menu(
        request: Request,
        target_menu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для удаления определенного меню."""

    return await delete_menu_logic(request, target_menu_id, session, redis_client)
