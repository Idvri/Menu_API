from .menu import CreateMenuSchema
from .universal import DefaultModelSchema


class DishSchema(DefaultModelSchema):
    """Pydantic схема для отображения блюда."""

    price: str


class CreateDishSchema(CreateMenuSchema):
    """Pydantic схема для создания блюда."""

    price: str
