from fastapi import APIRouter, Depends
from models.schemas import ReceptsShow, Recept, ReceptShow
from services.customersservices import CustomerService

customer_operation_router = APIRouter(prefix='/customer', tags=['Customer'])

@customer_operation_router.post('/addrecipe')
async def addRecipe(
    body: Recept, 
    service: CustomerService = Depends(),
):
    return await service.addRecipe(body)

@customer_operation_router.get('/list_recipe/', response_model= list[ReceptsShow])
async def allRecipe(
    limit: int = 100,
    service: CustomerService = Depends(),
):
    return await service.allRecipe(limit = limit)

@customer_operation_router.get('/getrecipe/', response_model= ReceptShow)
async def getRecipe(
    id: int,
    service: CustomerService = Depends(),
):
    return await service.getRecipe(id = id)

@customer_operation_router.get('/list_recipe_by_ingridients/')
async def filterByIngridients(
    ingridient: str,
    limit: int = 100,
    service: CustomerService = Depends(),
) -> list[ReceptsShow]|None:
    return await service.filterByIngridients(body = ingridient, limit = limit)

@customer_operation_router.put('/editRecipe/')
async def editRecipe(
    body: ReceptShow,
    service: CustomerService = Depends(),
):
    return await service.editRecipe(body = body)

@customer_operation_router.delete('/deleterecipe')
async def deleteRecipe(
    id: int,
    service: CustomerService = Depends(),
):
    return await service.deleteRecipe(id)