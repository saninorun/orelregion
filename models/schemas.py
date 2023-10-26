
import re
import datetime
from pydantic import BaseModel, ConfigDict, constr, conint, validator, confloat
from fastapi import HTTPException, status


LETTER_MATCH_PATTERN = re.compile(r'^[а-яА-Яa-zA-Z0-9Ёё\- ,.?()/!—]+$')
ERROR_INPUT_USER = HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Ошибка! Требуется использовать только алфавитные символы!'
            )

class Steps(BaseModel):
    step: str
    description: str
    duration: int
    
    @validator('step', 'description')
    def validate_first_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise ERROR_INPUT_USER
        return value.capitalize()

class Ingridients(BaseModel):
    title_ingridients: str
    quantity: confloat(gt=0)

    @validator('title_ingridients')
    def validate_first_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise ERROR_INPUT_USER
        return value.capitalize()

class Recept(BaseModel):
    title: str
    ingridients: list[Ingridients]
    steps: list[Steps]

    @validator('title')
    def validate_first_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise ERROR_INPUT_USER
        return value.capitalize()


class Show(BaseModel):
    model_config = ConfigDict(from_attributes = True)


class ReceptsShow(Show):
    id: int
    title: str

class StepsShow(BaseModel):
    id: int
    step: str
    description: str

class ReceptShow(Show):
    id: int
    title: str
    ingridients: list[Ingridients]
    steps: list[Steps]