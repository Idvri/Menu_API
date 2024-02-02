from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from src import get_async_session
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
):
    """Эндпойнт для получения подменю определенного меню."""

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
):
    """Эндпойнт для создания подменю."""

    try:
        submenu = await create_db_obj(target_menu_id, data, session)
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
):
    """Эндпойнт для изменения подменю."""

    submenu = await get_submenu_db(target_submenu_id, session)
    check_db_obj(submenu, 'submenu')
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
        target_submenu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для удаления подменю."""

    submenu = await get_submenu_db(target_submenu_id, session)
    check_db_obj(submenu, 'submenu')
    for dish in submenu.dishes:
        await session.delete(dish)
    await session.delete(submenu)
    await session.commit()
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
