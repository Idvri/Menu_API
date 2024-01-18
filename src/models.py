from typing import List

from sqlalchemy import String, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src import Base, INT_PK


class DefaultModel:
    """Модель с переиспользуемыми полями для других моделей."""

    id: Mapped[INT_PK]
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Text] = mapped_column(Text)


class Menu(DefaultModel, Base):
    """Модель меню."""

    __tablename__ = 'menu'

    submenus: Mapped[List['SubMenu']] = relationship(back_populates='menu', lazy=False)


class SubMenu(DefaultModel, Base):
    """Модель подменю."""

    __tablename__ = 'submenu'

    menu_id: Mapped[int] = mapped_column(ForeignKey('menu.id', ondelete='CASCADE'))
    menu: Mapped['Menu'] = relationship(back_populates='submenus')

    dishes: Mapped[List['Dish']] = relationship(back_populates='submenu', lazy=False)


class Dish(DefaultModel, Base):
    """Модель блюда."""

    __tablename__ = 'dish'

    price: Mapped[float] = mapped_column(Float)

    submenu_id: Mapped[int] = mapped_column(ForeignKey('submenu.id', ondelete='CASCADE'))
    submenu: Mapped['SubMenu'] = relationship(back_populates='dishes', lazy=False)
