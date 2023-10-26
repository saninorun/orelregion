import sqlalchemy
import datetime

from sqlalchemy import Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship



class Base(DeclarativeBase):
    pass

class RecipeBD(Base):
    '''Класс модели для создания и работы с таблицами БД'''

    __tablename__ = 'recipes'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    step: Mapped[list['StepsBD']] = relationship(
                                                back_populates='recipe_name', 
                                                cascade="all, delete", 
                                                passive_deletes=True
                                                )
    list_ingridients: Mapped[list['ListIngridientBD']] = relationship(
                                                back_populates='recipe_name', 
                                                cascade="all, delete", 
                                                passive_deletes=True
                                                )

class IngridientBD(Base):

    __tablename__ = 'ingridients'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    list_ingridients: Mapped[list['ListIngridientBD']] = relationship(
                                                back_populates='ingridient_name', 
                                                cascade="all, delete", 
                                                passive_deletes=True
                                                )

class StepsBD(Base):

    __tablename__ = 'steps'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    recipe_id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey('recipes.id', 
                                                                 onupdate='CASCADE', 
                                                                 ondelete="CASCADE"
                                                                 ), nullable=False,
                                            )
    recipe_name: Mapped['RecipeBD'] = relationship(back_populates='step')

class ListIngridientBD(Base):

    __tablename__ = 'listofingridients'

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey(
                                                                'recipes.id', 
                                                                onupdate='CASCADE', 
                                                                ondelete="CASCADE"
                                                                ), nullable=False,
                                            )
    ingridients_id: Mapped[str] = mapped_column(sqlalchemy.ForeignKey(
                                                                      'ingridients.id', 
                                                                      onupdate='CASCADE', 
                                                                      ondelete="CASCADE"
                                                                      ), nullable=False,
                                                )
    quantity: Mapped[float] = mapped_column(nullable=False)
    recipe_name: Mapped['RecipeBD'] = relationship(back_populates='list_ingridients')
    ingridient_name: Mapped['IngridientBD'] = relationship(back_populates='list_ingridients')