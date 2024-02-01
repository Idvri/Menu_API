from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND
from starlette.responses import JSONResponse

from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_async_session
from src.schemas import MessageSchema, DishSchema, CreateDishSchema
from src.utils import get_dishes_db, create_db_obj, get_dish_db

router = APIRouter(
    prefix='/dishes',
)


@router.get(
    '/',
    response_model=List[DishSchema],
    status_code=HTTP_200_OK,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Dish'],
)
async def get_dishes(
        target_submenu_id: UUID,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения блюд определенного подменю."""

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
        target_submenu_id: UUID,
        data: CreateDishSchema,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для создания подменю."""

    try:
        dish = await create_db_obj(target_submenu_id, data, session)
    except IntegrityError:
        return JSONResponse(content={'detail': 'submenu not found'}, status_code=HTTP_404_NOT_FOUND)
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
):
    """Эндпойнт для получения подменю."""

    dish = await get_dish_db(target_dish_id, session)
    return dish


@router.patch(
    '/{target_dish_id}',
    response_model=DishSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Dish'],
)
async def update_dish(
        target_dish_id: UUID,
        data: CreateDishSchema,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для изменения блюда."""

    dish = await get_dish_db(target_dish_id, session)
    dish.title = data.title
    dish.description = data.description
    dish.price = data.price
    await session.commit()
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
        target_dish_id: UUID,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для удаления блюда."""

    dish = await get_dish_db(target_dish_id, session)
    await session.delete(dish)
    await session.commit()
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
