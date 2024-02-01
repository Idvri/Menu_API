from .menu import MenuSchema, CreateMenuSchema


class DishSchema(MenuSchema):
    """Pydantic схема для отображения блюда."""

    price: str


class CreateDishSchema(CreateMenuSchema):
    """Pydantic схема для создания блюда."""

    price: str
