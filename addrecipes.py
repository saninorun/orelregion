import sqlalchemy
import asyncio
from pydantic import TypeAdapter
from fastapi import HTTPException, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import Recept, Steps, ReceptShow, Ingridients, Steps, ReceptsShow
from dbtable.dbmodel import RecipeBD, ListIngridientBD, IngridientBD, StepsBD
from core.database import get_session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from settings import settings
from baserecies import recipe as allrecipe

engine = create_async_engine(
    f'postgresql+asyncpg://{settings.db_user}:{settings.db_passw}@{settings.db_host}:{settings.db_port}/{settings.db_name}',
    echo=False,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def _getIngridient(title: str):
        query = select(IngridientBD).where(IngridientBD.title == title)
        async with async_session() as session:
            async with session.begin():
                rezult = await session.execute(query)
                rezult = rezult.first()
                await session.close()
        return rezult[0] if rezult else None

async def _ingridStepsRecipe(
        *, 
        recipe: RecipeBD,
        ingridients: list[Ingridients], 
        steps: list[Steps],            
    ) -> (list[ListIngridientBD], list[StepsBD]):
    components = []
    for item in ingridients:
        uniq_ingridients = await _getIngridient(title = item.title_ingridients)
        components.append(ListIngridientBD(
                recipe_name = recipe,
                ingridient_name = uniq_ingridients if uniq_ingridients else IngridientBD(
                                                                                title = item.title_ingridients,
                                                                                ),
                quantity = item.quantity,
                )
            )
    liststeps = []
    for item in steps:
        liststeps.append(StepsBD(
            title = item.step,
            description = item.description,
            duration = item.duration,
            recipe_name = recipe,
            )
        )
    return (components, liststeps)

async def _addToBD(
        *,
        ingridients: list[ListIngridientBD],
        steps: list[StepsBD],
        ):
    try:
        async with async_session() as session:
            async with session.begin():
                session.add_all(ingridients)
                session.add_all(steps)
    except sqlalchemy.exc.OperationalError:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Ошибка связи с базой данных! "
                )
    except sqlalchemy.exc.DBAPIError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Ошибка добавления в базу данных! "
                )
    return HTTPException(
                status_code=status.HTTP_200_OK, 
                detail="Рецепт успешно добавлен/обновлен в базе!"
                )

async def addRecipe(body: Recept):
    recipe = RecipeBD(title = body.title,)
    listingridient, liststeps = await _ingridStepsRecipe(
                                                recipe = recipe,
                                                ingridients = body.ingridients,
                                                steps = body.steps,
                                            )
    rezult = await _addToBD(
                            ingridients = listingridient,
                            steps = liststeps,
                        )
    return rezult

async def main():
    ta = TypeAdapter(list[Recept])
    m = ta.validate_python(allrecipe)
    for item in m:
        await addRecipe(item)

asyncio.run(main())

