from uuid import UUID

from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from src import get_async_redis_client, get_async_session
from src.logic import (
    create_submenu_logic,
    delete_submenu_logic,
    get_submenu_logic,
    get_submenus_logic,
    update_submenu_logic,
)
from src.schemas import CreateSubmenuSchema, MessageSchema, SubmenuSchema

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
        request: Request,
        target_menu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения подменю определенного меню."""

    return await get_submenus_logic(request, target_menu_id, session, redis_client)


@router.post(
    '/',
    response_model=SubmenuSchema,
    status_code=HTTP_201_CREATED,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Submenu'],
)
async def create_submenu(
        request: Request,
        target_menu_id: UUID,
        data: CreateSubmenuSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для создания подменю."""

    return await create_submenu_logic(request, target_menu_id, data, session, redis_client)


@router.get(
    '/{target_submenu_id}',
    response_model=SubmenuSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Submenu'],
)
async def get_submenu(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для получения подменю."""

    return await get_submenu_logic(request, target_menu_id, target_submenu_id, session, redis_client)


@router.patch(
    '/{target_submenu_id}',
    response_model=SubmenuSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Submenu'],
)
async def update_submenu(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        data: CreateSubmenuSchema,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для изменения подменю."""

    return await update_submenu_logic(request, target_menu_id, target_submenu_id, data, session, redis_client)


@router.delete(
    '/{target_submenu_id}',
    responses={
        HTTP_200_OK: {'model': MessageSchema},
        HTTP_404_NOT_FOUND: {'model': MessageSchema},
    },
    tags=['Submenu'],
)
async def delete_submenu(
        request: Request,
        target_menu_id: UUID,
        target_submenu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
        redis_client: Redis = Depends(get_async_redis_client),
):
    """Эндпойнт для удаления подменю."""

    return await delete_submenu_logic(request, target_menu_id, target_submenu_id, session, redis_client)
