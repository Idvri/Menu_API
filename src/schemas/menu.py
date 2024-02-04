from uuid import UUID

from pydantic import BaseModel


class MenuSchema(BaseModel):
    """Pydantic схема для отображения меню."""

    id: UUID
    title: str
    description: str


class CreateMenuSchema(BaseModel):
    """Pydantic схема для создания меню."""

    id: UUID | None = None
    title: str
    description: str


class MenuSchemaWithCounters(MenuSchema):
    """Pydantic схема для отображения меню c кол-вом подменю и блюд."""

    submenus_count: int
    dishes_count: int
