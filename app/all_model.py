from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional
from bson import ObjectId
# custom type with __get_pydantic_core_schema__
from pyobjectid import PyObjectId

# ---------------------------
# Users
# ---------------------------
# ** USED ONLY FOR Account CREATION


class UserForm(BaseModel):
    email: Optional[str] = None
    username: str
    name: Optional[str] = None
    hashed_password: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            date: str
        }  # type: ignore


"""
User Authentication only needed for token auth in services/auth.py
"""


class UserAuth(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    disabled: Optional[bool] = Field(default=False)
    is_admin: Optional[bool] = False

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


# ---------------------------
# User Profiles
# ---------------------------
class UserProfileCreate(BaseModel):
    user_id: PyObjectId  # references a _id in users
    major: Optional[str] = None
    year: Optional[int] = None
    interests: List[str] = []
    badges: List[str] = []
    personality_type: Optional[str] = None


class UserProfileDB(UserProfileCreate):
    id: PyObjectId = Field(..., alias="_id")
    profile_created_at: datetime = Field(...)

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }


# ---------------------------
# Events
# ---------------------------
class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    tags: List[str] = []


class EventDB(EventCreate):
    id: PyObjectId = Field(..., alias="_id")
    created_at: datetime = Field(...)

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }


# ---------------------------
# Clubs
# ---------------------------
class ClubCreate(BaseModel):
    name: str
    description: Optional[str] = None
    meeting_times: Optional[str] = None
    tags: List[str] = []
    contact_email: Optional[str] = None


class ClubDB(ClubCreate):
    id: PyObjectId = Field(..., alias="_id")
    created_at: datetime = Field(...)

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }


# ---------------------------
# Attendances
# ---------------------------
class AttendanceCreate(BaseModel):
    user_id: PyObjectId
    event_id: PyObjectId
    scanned_at: Optional[datetime] = None
    # Optional inline feedback data (e.g., rating, comments)
    feedback: Optional[dict] = None


class AttendanceDB(AttendanceCreate):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }


# ---------------------------
# Memberships
# ---------------------------
class MembershipCreate(BaseModel):
    user_id: PyObjectId
    club_id: PyObjectId
    joined_at: Optional[datetime] = None


class MembershipDB(MembershipCreate):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }


# ---------------------------
# Feedback
# ---------------------------
class FeedbackCreate(BaseModel):
    user_id: PyObjectId
    target_type: str  # e.g., "event", "club", "resource"
    target_id: PyObjectId
    rating: Optional[int] = None
    comment: Optional[str] = None
    created_at: datetime = Field(...)


class FeedbackDB(FeedbackCreate):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }


# ---------------------------
# Resources
# ---------------------------
class ResourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    contact_info: Optional[str] = None
    tags: List[str] = []


class ResourceDB(ResourceCreate):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
