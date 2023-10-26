import uvicorn
from fastapi import FastAPI
from api import router
from settings import settings


app = FastAPI()
app.include_router(router)

# if __name__ == '__main__':
#     uvicorn.run(
#         'main:app',
#         port=settings.server_port,
#         host=settings.server_host,
#         reload=True
#     ) 