from uuid import UUID

from fastapi import APIRouter, Depends

from typing import List

from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND
from starlette.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src import Menu, get_async_session, MenuSchema, CreateMenuSchema, MessageSchema, MenuSchemaWithCounters, \
    get_menu_db

router = APIRouter(
    prefix='/menus',
)


@router.get(
    '/',
    response_model=List[MenuSchema],
    tags=['Menu'],
)
async def get_menus(
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения всех меню."""

    query = select(Menu)
    result = await session.execute(query)
    menus = result.scalars().unique().all()
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

    if data.id:
        # noinspection PyArgumentList
        menu = Menu(id=data.id, title=data.title, description=data.description)
    else:
        # noinspection PyArgumentList
        menu = Menu(title=data.title, description=data.description)
    session.add(menu)
    await session.commit()
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

    try:
        menu = await get_menu_db(target_menu_id, session)
    except NoResultFound:
        return JSONResponse(content={'detail': 'menu not found'}, status_code=HTTP_404_NOT_FOUND)
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

    query = select(Menu).where(Menu.id == target_menu_id)
    result = await session.execute(query)
    try:
        menu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={'detail': 'menu not found'}, status_code=HTTP_404_NOT_FOUND)
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

    query = select(Menu).where(Menu.id == target_menu_id)
    result = await session.execute(query)
    try:
        menu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={'detail': 'menu not found'}, status_code=HTTP_404_NOT_FOUND)
    await session.delete(menu)
    await session.commit()
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
