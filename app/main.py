from fastapi import FastAPI
import all_api
import authentication


app = FastAPI()

# app.include_router(user_api.router)
app.include_router(all_api.router)
app.include_router(authentication.router)
