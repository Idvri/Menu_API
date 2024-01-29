from uuid import UUID

from fastapi import APIRouter, Depends

from typing_extensions import List

from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND
from starlette.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_async_session, CreateSubmenuSchema, Submenu, MessageSchema, SubmenuSchema, \
    SubmenuSchemaWithCounter, get_submenu_db

router = APIRouter(
    prefix='/submenus',
)


@router.get(
    '/',
    response_model=List[SubmenuSchema],
    status_code=HTTP_200_OK,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Submenu'],

)
async def get_submenus(
        target_menu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения подменю определенного меню."""

    query = select(Submenu).where(Submenu.menu_id == target_menu_id)
    result = await session.execute(query)
    try:
        submenus = result.scalars().unique().all()
    except NoResultFound:
        return JSONResponse(content={'detail': 'menu not found'}, status_code=HTTP_404_NOT_FOUND)
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
):
    """Эндпойнт для создания подменю."""

    if data.id:
        # noinspection PyArgumentList
        submenu = Submenu(id=data.id, title=data.title, description=data.description, menu_id=target_menu_id)
    else:
        # noinspection PyArgumentList
        submenu = Submenu(title=data.title, description=data.description, menu_id=target_menu_id)
    session.add(submenu)
    try:
        await session.commit()
    except IntegrityError:
        return JSONResponse(content={'detail': 'menu not found'}, status_code=HTTP_404_NOT_FOUND)
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
):
    """Эндпойнт для получения подменю."""

    try:
        submenu = await get_submenu_db(target_submenu_id, session)
    except NoResultFound:
        return JSONResponse(content={'detail': 'submenu not found'}, status_code=HTTP_404_NOT_FOUND)
    return submenu


@router.patch(
    '/{target_submenu_id}',
    response_model=SubmenuSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Submenu'],
)
async def update_submenu(
        target_menu_id: UUID,
        target_submenu_id: UUID,
        data: CreateSubmenuSchema,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для изменения подменю."""

    query = select(Submenu).where(Submenu.menu_id == target_menu_id, Submenu.id == target_submenu_id)
    result = await session.execute(query)
    try:
        submenu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={'detail': 'submenu not found'}, status_code=HTTP_404_NOT_FOUND)
    submenu.title = data.title
    submenu.description = data.description
    await session.commit()
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
):
    """Эндпойнт для удаления подменю."""

    query = select(Submenu).where(Submenu.menu_id == target_menu_id, Submenu.id == target_submenu_id)
    result = await session.execute(query)
    try:
        submenu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={'detail': 'submenu not found'}, status_code=HTTP_404_NOT_FOUND)
    for dish in submenu.dishes:
        await session.delete(dish)
    await session.delete(submenu)
    await session.commit()
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
