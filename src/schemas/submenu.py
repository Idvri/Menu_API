from .menu import CreateMenuSchema
from .universal import DefaultModelSchema


class SubmenuSchema(DefaultModelSchema):
    """Pydantic схема для отображения подменю."""

    dishes_count: int = 0


class CreateSubmenuSchema(CreateMenuSchema):
    """Pydantic схема для создания подменю."""
    pass
