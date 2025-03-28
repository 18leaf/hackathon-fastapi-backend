from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional
from bson import ObjectId


# ** USED ONLY FOR Account CREATION
class UserForm(BaseModel):
    email: str | None = None
    username: str
    name: str | None = None
    hashed_password: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders: {
            date: str
        }  # type: ignore


"""
User Authentication only needed for token auth in services/auth.py
"""


class UserAuth(BaseModel):
    id: ObjectId = Field(..., alias="_id")
    email: str | None = Field(default=None)
    username: str | None = Field(default=None)
    disabled: bool | None = Field(default=False)
    is_admin: bool | None = False

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }


class UserAuthPass(UserAuth):
    hashed_password: str

    class Config:
        extra = 'allow'
