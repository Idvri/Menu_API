from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src import DefaultModel, Dish, Menu, Submenu, get_async_session
from src.schemas import CreateDishSchema, CreateMenuSchema, CreateSubmenuSchema


async def create_db_obj(
        obj_id: UUID | None = None,
        data: BaseModel = CreateMenuSchema,
        session: AsyncSession = Depends(get_async_session)
) -> Menu | Submenu | Dish:
    """Универсальная функция для создания меню/подменю/блюда."""

    if isinstance(data, CreateSubmenuSchema):
        if data.id:
            # noinspection PyArgumentList
            stmt = Submenu(id=data.id, title=data.title, description=data.description, menu_id=obj_id)
        else:
            # noinspection PyArgumentList
            stmt = Submenu(title=data.title, description=data.description, menu_id=obj_id)
    elif isinstance(data, CreateDishSchema):
        if data.id:
            # noinspection PyArgumentList
            stmt = Dish(
                id=data.id,
                title=data.title,
                description=data.description,
                price=data.price,
                submenu_id=obj_id
            )
        else:
            # noinspection PyArgumentList
            stmt = Dish(
                title=data.title,
                description=data.description,
                price=data.price,
                submenu_id=obj_id
            )
    else:
        if data.id:
            # noinspection PyArgumentList
            stmt = Menu(id=data.id, title=data.title, description=data.description)
        else:
            # noinspection PyArgumentList
            stmt = Menu(title=data.title, description=data.description)
    session.add(stmt)
    await session.commit()
    return stmt


def check_db_obj(obj: DefaultModel | tuple, name: str) -> None:
    """Универсальная функция для проверки существования полученного объекта,
    передаёт исключению аргумент в виде названия/типа объекта для дальнейших действий."""

    if not obj:
        NoResultFound.args = name
        raise NoResultFound
