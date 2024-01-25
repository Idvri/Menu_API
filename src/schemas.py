from typing import Text, Optional

from uuid import UUID

from pydantic import BaseModel


class MenuSchema(BaseModel):
    """Pydantic схема для отображения меню."""

    id: UUID
    title: str
    description: Text


class CreateMenuSchema(BaseModel):
    """Pydantic схема для создания меню."""

    id: Optional[UUID] = None
    title: str
    description: Text


class MenuSchemaWithCounters(MenuSchema):
    """Pydantic схема для отображения меню c кол-вом подменю и блюд."""

    submenus_count: int
    dishes_count: int


class SubmenuSchema(MenuSchema):
    """Pydantic схема для отображения подменю."""
    pass


class CreateSubmenuSchema(CreateMenuSchema):
    """Pydantic схема для создания подменю."""
    pass


class SubmenuSchemaWithCounter(MenuSchema):
    """Pydantic схема для отображения подменю c кол-вом блюд."""

    dishes_count: int


class DishSchema(MenuSchema):
    """Pydantic схема для отображения блюда."""

    price: str


class CreateDishSchema(CreateMenuSchema):
    """Pydantic схема для создания блюда."""

    price: str


class MessageSchema(BaseModel):
    """Pydantic схема для отображения простых сообщений."""

    detail: str
