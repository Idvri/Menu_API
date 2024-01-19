from typing import Text, List
from uuid import UUID

from pydantic import BaseModel


class CreateMenuSchema(BaseModel):
    """Pydantic схема для создания меню."""

    title: str
    description: Text


class MenuSchema(BaseModel):
    """Pydantic схема для отображения меню."""

    id: UUID
    title: str
    description: Text


class MenuSchemaWithCounters(MenuSchema):
    """Pydantic схема для отображения меню c кол-вом подменю и блюд."""

    submenus_count: int
    dishes_count: int


class SubmenuSchemaWithCounter(MenuSchema):
    """Pydantic схема для отображения подменю c кол-вом блюд."""

    dishes_count: int


class CreateSubmenuSchema(CreateMenuSchema):
    """Pydantic схема для создания подменю."""
    pass


class SubmenuSchema(MenuSchema):
    """Pydantic схема для отображения подменю."""
    pass


class MenuSubmenusSchema(MenuSchema):
    """Pydantic схема для отображения подменю в меню."""

    submenus: List[SubmenuSchema]


class DishSchema(MenuSchema):
    """Pydantic схема для отображения блюда."""

    price: str


class CreateDishSchema(CreateMenuSchema):
    """Pydantic схема для создания блюда."""

    price: str


class SubmenuDishesSchema(SubmenuSchema):
    """Pydantic схема для отображения блюд подменю."""

    dishes: List[DishSchema]


class MessageSchema(BaseModel):
    """Pydantic схема для отображения простых сообщений."""

    detail: str
