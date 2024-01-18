from typing import List, Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src import Base, INT_PK


class DefaultModel:
    """Модель с переиспользуемыми полями для других моделей."""

    id: Mapped[INT_PK]
    name: Mapped[str] = mapped_column(
        String
    )


class Menu(DefaultModel, Base):
    """Модель меню."""

    __tablename__ = 'menu'

    submenus: Mapped[List['SubMenu']] = relationship(back_populates="menu", lazy=False)


class SubMenu(DefaultModel, Base):
    """Модель подменю."""

    __tablename__ = 'submenu'

    menu_id: Mapped[Optional[int]] = mapped_column(ForeignKey("menu.id"))
    menu: Mapped[Optional['Menu']] = relationship(back_populates="products")

    dishes: Mapped[List['Dish']] = relationship(back_populates="submenu", lazy=False)


class Dish(DefaultModel, Base):
    """Модель блюда."""

    __tablename__ = 'dish'

    sub_menu_id: Mapped[Optional[int]] = mapped_column(ForeignKey("submenu.id"))
    sub_menu: Mapped[Optional['SubMenu']] = relationship(back_populates="dishes", lazy=False)
