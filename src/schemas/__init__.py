from .menu import MenuSchema, CreateMenuSchema
from .submenu import SubmenuSchema, CreateSubmenuSchema
from .dish import DishSchema, CreateDishSchema
from .universal import DefaultModelSchema, MessageSchema

__all__ = [
    'MenuSchema', 'CreateMenuSchema',

    'SubmenuSchema', 'CreateSubmenuSchema',

    'DishSchema', 'CreateDishSchema',

    'DefaultModelSchema', 'MessageSchema',
]
