import sqlalchemy
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import Recept, Steps, ReceptShow, Ingridients, Steps, ReceptsShow
from dbtable.dbmodel import RecipeBD, ListIngridientBD, IngridientBD, StepsBD
from core.database import get_session


class CustomerService:
    
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
   
    async def _getRecipeName(self, *, title: str = None, id: int = None) -> RecipeBD:
        query = select(RecipeBD).where(RecipeBD.title == title if title else RecipeBD.id == id)
        async with self.session.begin():
            rezult = await self.session.execute(query)
            rezult = rezult.first()
            await self.session.close()
        return rezult[0] if rezult else None
    
    async def _getIngridients(self, id: int) -> list[Ingridients]:
        query = select(
                         IngridientBD.title, ListIngridientBD.quantity,
                        ).join(RecipeBD,).join(IngridientBD).where(RecipeBD.id == id)
        async with self.session.begin():
            rezult = await self.session.execute(query)
            rezult = rezult.all()
            if rezult:
                rezult = [Ingridients(
                                    title_ingridients = i[0], 
                                    quantity = i[1]
                                    ) for i in rezult]
            await self.session.close()
        return rezult
    
    async def _getSteps(self, id: int) -> list[Steps]:
        query = select(
                        StepsBD.title, StepsBD.description, StepsBD.duration,
                        ).join(RecipeBD,).where(RecipeBD.id == id)
        async with self.session.begin():
            rezult = await self.session.execute(query)
            rezult = rezult.all()
            rezult = [Steps(step = i[0], description = i[1], duration = i[2]) for i in rezult]
            await self.session.close()
        return rezult
    
    async def _getIngridient(self, title: str):
        query = select(IngridientBD).where(IngridientBD.title == title)
        async with self.session.begin():
            rezult = await self.session.execute(query)
            rezult = rezult.first()
            await self.session.close()
        return rezult[0] if rezult else None
    
    async def _ingridStepsRecipe(
            self,
            *, 
            recipe: RecipeBD,
            ingridients: list[Ingridients], 
            steps: list[Steps],            
        ) -> (list[ListIngridientBD], list[StepsBD]):
        components = []
        for item in ingridients:
            uniq_ingridients = await self._getIngridient(title = item.title_ingridients)
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
            self, 
            *,
            recipe: RecipeBD|None = None,
            recipe_title: str|None = None,
            ingridients: list[ListIngridientBD],
            steps: list[StepsBD],
            ):
        try:
            async with self.session.begin():
                if recipe:
                    await self.session.execute(update(RecipeBD).where(RecipeBD.id == recipe.id).values(title = recipe_title))
                    await self.session.execute(delete(ListIngridientBD).where(ListIngridientBD.recipe_name == recipe))
                    await self.session.execute(delete(StepsBD).where(StepsBD.recipe_name == recipe))
                self.session.add_all(ingridients)
                self.session.add_all(steps)
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

    async def addRecipe(self, body: Recept):
        if await self._getRecipeName(title = body.title):
            raise HTTPException(
                    status_code=status.HTTP_302_FOUND, 
                    detail="Такой рецепт уже добавлен в базу."
                )
        recipe = RecipeBD(title = body.title,)
        listingridient, liststeps = await self._ingridStepsRecipe(
                                                    recipe = recipe,
                                                    ingridients = body.ingridients,
                                                    steps = body.steps,
                                                )
        rezult = await self._addToBD(
                                ingridients = listingridient,
                                steps = liststeps,
                            )
        return rezult
    
    async def allRecipe(self, limit: int):
        query = select(RecipeBD.id, RecipeBD.title).limit(limit)
        async with self.session.begin():
            rezult = await self.session.execute(query)
            rezult = rezult.all()
        return rezult
    
    async def filterByIngridients(self, body: str, limit: int):
        query = select(RecipeBD.id, RecipeBD.title
                       ).join(ListIngridientBD
                              ).join(IngridientBD
                                     ).where(IngridientBD.title.like(f'%{body.capitalize()}%')
                                             ).limit(limit)
        async with self.session.begin():
            rezult = await self.session.execute(query)
            rezult = rezult.all()
        return rezult if rezult else None
            

    async def getRecipe(self, id: int):
        if not await self._getRecipeName(id = id):
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Рецепт с таким номером отсутствует в базе данных!"
                )
        recipe_title = await self._getRecipeName(id = id)
        recipe_ingridients = await self._getIngridients(id = id)
        recipe_steps = await self._getSteps(id = id)

        rezult = ReceptShow(
            id = recipe_title.id,
            title = recipe_title.title,
            ingridients = recipe_ingridients,
            steps = recipe_steps
        )
        return rezult
    
    async def editRecipe(self, body: ReceptShow):
        if not await self._getRecipeName(id = body.id):
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Рецепт с таким номером отсутствует в базе данных!"
                )
        recipe = await self._getRecipeName(id = body.id)
        listingridient, liststeps = await self._ingridStepsRecipe(
                                            recipe = recipe,
                                            ingridients = body.ingridients,
                                            steps = body.steps,
                                        )
        rezult = await self._addToBD(
                    recipe = recipe,
                    recipe_title = body.title,
                    ingridients = listingridient,
                    steps = liststeps,
                )
        return rezult

    async def deleteRecipe(self, id: int):
        if not await self._getRecipeName(id = id):
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Рецепт с таким номером отсутствует в базе данных!"
                )
        try:
            async with self.session.begin():
                rezult = await self.session.execute(delete(RecipeBD).where(RecipeBD.id == id))
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
                    detail="Рецепт удален из базы!"
                    ) if rezult else None
    


