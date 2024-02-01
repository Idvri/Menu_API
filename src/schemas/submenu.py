from .menu import MenuSchema, CreateMenuSchema


class SubmenuSchema(MenuSchema):
    """Pydantic схема для отображения подменю."""
    pass


class CreateSubmenuSchema(CreateMenuSchema):
    """Pydantic схема для создания подменю."""
    pass


class SubmenuSchemaWithCounter(SubmenuSchema):
    """Pydantic схема для отображения подменю c кол-вом блюд."""

    dishes_count: int
