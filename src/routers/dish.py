from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND
from starlette.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_async_session, MessageSchema, DishSchema, CreateDishSchema, Dish

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

    query = select(Dish).where(Dish.submenu_id == target_submenu_id)
    result = await session.execute(query)
    try:
        dishes = result.scalars().unique().all()
    except NoResultFound:
        return JSONResponse(content=[], status_code=HTTP_200_OK)
    if not dishes:
        return JSONResponse(content=dishes, status_code=HTTP_200_OK)
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

    # noinspection PyArgumentList
    dish = Dish(title=data.title, description=data.description, price=data.price, submenu_id=target_submenu_id)
    session.add(dish)
    try:
        await session.commit()
    except IntegrityError:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=HTTP_404_NOT_FOUND)
    return dish


@router.get(
    '/{target_dish_id}',
    response_model=DishSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}},
    tags=['Dish'],
)
async def get_dish(
        target_submenu_id: UUID,
        target_dish_id: UUID,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения подменю."""

    query = select(Dish).where(Dish.submenu_id == target_submenu_id, Dish.id == target_dish_id)
    result = await session.execute(query)
    try:
        dish = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "dish not found"}, status_code=HTTP_404_NOT_FOUND)
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
):
    """Эндпойнт для изменения блюда."""

    query = select(Dish).where(Dish.submenu_id == target_submenu_id, Dish.id == target_dish_id)
    result = await session.execute(query)
    try:
        dish = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "dish not found"}, status_code=HTTP_404_NOT_FOUND)
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
        target_submenu_id: UUID,
        target_dish_id: UUID,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для удаления блюда."""

    query = select(Dish).where(Dish.submenu_id == target_submenu_id, Dish.id == target_dish_id)
    result = await session.execute(query)
    try:
        dish = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "dish not found"}, status_code=HTTP_404_NOT_FOUND)
    await session.delete(dish)
    await session.commit()
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
