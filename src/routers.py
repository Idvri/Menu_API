from fastapi import APIRouter
from typing import List

from fastapi import Depends

from starlette.status import HTTP_201_CREATED
from starlette.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import Menu, get_async_session, MenuSchema, CreateMenuSchema

menu_router = APIRouter(
    prefix='/api/v1',
    tags=['Menu'],
)


@menu_router.get('/menus', response_model=List[MenuSchema])
async def get_menus(
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для получения всех меню."""

    query = select(Menu)
    result = await session.execute(query)
    return result.scalars().unique().all()


@menu_router.post('/menus')
async def create_menu(
        data: CreateMenuSchema,
        session: AsyncSession = Depends(get_async_session),
):
    """Эндпойнт для создания меню."""

    # noinspection PyArgumentList
    menu = Menu(title=data.title, description=data.description)
    session.add(menu)
    await session.commit()
    data = {
        'id': str(menu.id),
        'title': menu.title,
        'description': menu.description
    }
    return JSONResponse(content=data, status_code=HTTP_201_CREATED)
