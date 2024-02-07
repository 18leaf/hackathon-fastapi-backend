from fastapi import FastAPI
from api import user_api
from services import authentication

app = FastAPI()

app.include_router(user_api.router)
app.include_router(authentication.router)