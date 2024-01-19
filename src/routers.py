from fastapi import APIRouter
from typing import List

from fastapi import Depends
from sqlalchemy.exc import NoResultFound, IntegrityError

from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND
from starlette.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import Menu, get_async_session, MenuSchema, CreateMenuSchema, CreateSubmenuSchema, Submenu, \
    MenuSubmenusSchema, MessageSchema, SubmenuSchema, SubmenuDishesSchema, DishSchema, CreateDishSchema, Dish, \
    MenuSchemaWithCounters, SubmenuSchemaWithCounter

menu_router = APIRouter(
    prefix='/api/v1',
    tags=['Menu'],
)


@menu_router.get(
    '/menus',
    response_model=List[MenuSchema]
)
async def get_menus(
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения всех меню."""

    query = select(Menu)
    result = await session.execute(query)
    menus = result.scalars().unique().all()
    if menus:
        for menu in menus:
            menu.id = str(menu.id)
    return menus


@menu_router.post(
    '/menus',
    response_model=MenuSchema,
    status_code=HTTP_201_CREATED
)
async def create_menu(
        data: CreateMenuSchema,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для создания меню."""

    # noinspection PyArgumentList
    menu = Menu(title=data.title, description=data.description)
    session.add(menu)
    await session.commit()
    menu.id = str(menu.id)
    return menu


@menu_router.get(
    '/menus/{menu_id}',
    response_model=MenuSchemaWithCounters,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}}
)
async def get_menu(
        menu_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения определенного меню."""

    query = select(Menu).where(Menu.id == menu_id)
    result = await session.execute(query)
    try:
        menu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "menu not found"}, status_code=HTTP_404_NOT_FOUND)
    menu.id = str(menu.id)
    menu.submenus_count = len(menu.submenus)
    menu.dishes_count = sum(len(submenu.dishes) for submenu in menu.submenus)
    return menu


@menu_router.patch(
    '/menus/{menu_id}',
    response_model=MenuSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}}
)
async def update_menu(
        menu_id: int,
        data: CreateMenuSchema,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для изменения определенного меню."""

    query = select(Menu).where(Menu.id == menu_id)
    result = await session.execute(query)
    try:
        menu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "menu not found"}, status_code=HTTP_404_NOT_FOUND)
    menu.title = data.title
    menu.description = data.description
    await session.commit()
    menu.id = str(menu.id)
    return menu


@menu_router.delete(
    '/menus/{menu_id}',
    responses={
        HTTP_200_OK: {'model': MessageSchema},
        HTTP_404_NOT_FOUND: {'model': MessageSchema},
    }
)
async def delete_menu(
        menu_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для удаления определенного меню."""

    query = select(Menu).where(Menu.id == menu_id)
    result = await session.execute(query)
    try:
        menu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "menu not found"}, status_code=HTTP_404_NOT_FOUND)
    await session.delete(menu)
    await session.commit()
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)


@menu_router.get(
    '/menus/{menu_id}/submenus',
    response_model=MenuSubmenusSchema,
    status_code=HTTP_200_OK,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}}

)
async def get_submenus(
        menu_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения подменю определенного меню."""

    query = select(Menu).where(Menu.id == menu_id)
    result = await session.execute(query)
    try:
        menu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "menu not found"}, status_code=HTTP_404_NOT_FOUND)
    if not menu.submenus:
        return JSONResponse(content=menu.submenus, status_code=HTTP_200_OK)
    menu.id = str(menu.id)
    for submenu in menu.submenus:
        submenu.id = str(submenu.id)
    return menu


@menu_router.post(
    '/menus/{menu_id}/submenus',
    response_model=SubmenuSchema,
    status_code=HTTP_201_CREATED,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}}
)
async def create_submenu(
        menu_id: int,
        data: CreateSubmenuSchema,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для создания подменю."""

    # noinspection PyArgumentList
    submenu = Submenu(title=data.title, description=data.description, menu_id=menu_id)
    session.add(submenu)
    try:
        await session.commit()
    except IntegrityError:
        return JSONResponse(content={"detail": "menu not found"}, status_code=HTTP_404_NOT_FOUND)
    return submenu


@menu_router.get(
    '/menus/{menu_id}/submenus/{submenu_id}',
    response_model=SubmenuSchemaWithCounter,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}}
)
async def get_submenu(
        menu_id: int,
        submenu_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения подменю."""

    query = select(Submenu).where(Submenu.menu_id == menu_id, Submenu.id == submenu_id)
    result = await session.execute(query)
    try:
        submenu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=HTTP_404_NOT_FOUND)
    submenu.id = str(submenu.id)
    submenu.dishes_count = len(submenu.dishes)
    return submenu


@menu_router.patch(
    '/menus/{menu_id}/submenus/{submenu_id}',
    response_model=SubmenuSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}}
)
async def update_submenu(
        menu_id: int,
        submenu_id: int,
        data: CreateSubmenuSchema,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для изменения подменю."""

    query = select(Submenu).where(Submenu.menu_id == menu_id, Submenu.id == submenu_id)
    result = await session.execute(query)
    try:
        submenu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=HTTP_404_NOT_FOUND)
    submenu.title = data.title
    submenu.description = data.description
    await session.commit()
    return submenu


@menu_router.delete(
    '/menus/{menu_id}/submenus/{submenu_id}',
    responses={
        HTTP_200_OK: {'model': MessageSchema},
        HTTP_404_NOT_FOUND: {'model': MessageSchema},
    }
)
async def delete_submenu(
        menu_id: int,
        submenu_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для удаления подменю."""

    query = select(Submenu).where(Submenu.menu_id == menu_id, Submenu.id == submenu_id)
    result = await session.execute(query)
    try:
        submenu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=HTTP_404_NOT_FOUND)
    for dish in submenu.dishes:
        await session.delete(dish)
    await session.delete(submenu)
    await session.commit()
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)


@menu_router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=SubmenuDishesSchema,
    status_code=HTTP_200_OK,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}}

)
async def get_dishes(
        menu_id: int,
        submenu_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения блюд определенного подменю."""

    query = select(Submenu).where(Submenu.id == submenu_id, Submenu.menu_id == menu_id)
    result = await session.execute(query)
    try:
        submenu = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content=[], status_code=HTTP_200_OK)
    if not submenu.dishes:
        return JSONResponse(content=submenu.dishes, status_code=HTTP_200_OK)
    submenu.id = str(submenu.id)
    for dish in submenu.dishes:
        dish.id = str(dish.id)
        dish.price = str(dish.price)
    return submenu


@menu_router.post(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=DishSchema,
    status_code=HTTP_201_CREATED,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}}
)
async def create_dish(
        submenu_id: int,
        data: CreateDishSchema,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для создания подменю."""

    # noinspection PyArgumentList
    dish = Dish(title=data.title, description=data.description, price=data.price, submenu_id=submenu_id)
    session.add(dish)
    try:
        await session.commit()
    except IntegrityError:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=HTTP_404_NOT_FOUND)
    dish.id = str(dish.id)
    dish.price = str(dish.price)
    return dish


@menu_router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=DishSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}}
)
async def get_dish(
        submenu_id: int,
        dish_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения подменю."""

    query = select(Dish).where(Dish.submenu_id == submenu_id, Dish.id == dish_id)
    result = await session.execute(query)
    try:
        dish = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "dish not found"}, status_code=HTTP_404_NOT_FOUND)
    dish.id = str(dish.id)
    dish.price = str(dish.price)
    return dish


@menu_router.patch(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=SubmenuSchema,
    responses={HTTP_404_NOT_FOUND: {'model': MessageSchema}}
)
async def update_dish(
        submenu_id: int,
        dish_id: int,
        data: CreateDishSchema,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для изменения блюда."""

    query = select(Dish).where(Dish.submenu_id == submenu_id, Dish.id == dish_id)
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


@menu_router.delete(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    responses={
        HTTP_200_OK: {'model': MessageSchema},
        HTTP_404_NOT_FOUND: {'model': MessageSchema},
    }
)
async def delete_dish(
        submenu_id: int,
        dish_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для удаления блюда."""

    query = select(Dish).where(Dish.submenu_id == submenu_id, Dish.id == dish_id)
    result = await session.execute(query)
    try:
        dish = result.scalars().unique().one()
    except NoResultFound:
        return JSONResponse(content={"detail": "dish not found"}, status_code=HTTP_404_NOT_FOUND)
    await session.delete(dish)
    await session.commit()
    return JSONResponse(content={'message': 'Success.'}, status_code=HTTP_200_OK)
