from pydantic import BaseModel

from .universal import DefaultModelSchema


class MenuSchema(DefaultModelSchema):
    """Pydantic схема для отображения меню c кол-вом подменю и блюд."""

    submenus_count: int = 0
    dishes_count: int = 0


class CreateMenuSchema(BaseModel):
    """Pydantic схема для создания меню."""

    title: str
    description: str
