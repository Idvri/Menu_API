from .menu import CreateMenuSchema, MenuSchema


class DishSchema(MenuSchema):
    """Pydantic схема для отображения блюда."""

    price: str


class CreateDishSchema(CreateMenuSchema):
    """Pydantic схема для создания блюда."""

    price: str
