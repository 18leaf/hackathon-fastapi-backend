from db.mongodb import database
from models.user_model import UserAuth, UserAuthPass, UserForm
from bson.objectid import ObjectId
from datetime import date

user_collection = database.users


async def get_user(user_id: str) -> UserAuth:
    result = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not result:
        return False
    return UserAuth(**result)


async def get_user_by_username(username: str) -> UserAuthPass:
    result = await user_collection.find_one({"username": username})
    if not result:
        return False
    return UserAuthPass(**result)


async def get_user_by_email(email: str):
    return await user_collection.find_one({"email": email})


async def create_user(user_data: UserForm):
    user = user_data.model_dump()
    result = await user_collection.insert_one(user)
    new_user = await user_collection.find_one({"_id": result.inserted_id})
    return new_user

