from typing import Text

from pydantic import BaseModel


class CreateMenuSchema(BaseModel):
    """Pydantic схема для создания меню."""

    title: str
    description: Text


class MenuSchema(BaseModel):
    """Pydantic схема для отображения меню."""

    id: int
    title: str
    description: Text
