from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from src import get_async_session
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
):
    """Эндпойнт для получения всех меню."""

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
):
    """Эндпойнт для создания меню."""
    menu = await create_db_obj(data=data, session=session)
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
):
    """Эндпойнт для получения определенного меню."""

    menu = await get_menu_db_with_counters(target_menu_id, session)
    check_db_obj(menu, 'menu')
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
):
    """Эндпойнт для изменения определенного меню."""

    menu = await get_menu_db(target_menu_id, session)
    check_db_obj(menu, 'menu')
    menu.title = data.title
    menu.description = data.description
    await session.commit()
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
):
    """Эндпойнт для удаления определенного меню."""

    menu = await get_menu_db(target_menu_id, session)
    check_db_obj(menu, 'menu')
    await session.delete(menu)
    await session.commit()
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
