# custom ObjectId type with __get_pydantic_core_schema__
from pyobjectid import PyObjectId
from bson import ObjectId
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field


# NOTE:
# • “Create” models omit fields that are auto-generated on insertion (like created_at).
# • “DB” models require those fields. In your CRUD layer, after insertion,
#   ensure you inject required fields (or use model_dump(by_alias=True)) when re-creating a DB model.


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

    class Config:
        arbitrary_types_allowed = True
        # When dumping, use aliases if needed: model_dump(by_alias=True)
        json_encoders = {ObjectId: str}


class UserProfileDB(UserProfileCreate):
    id: PyObjectId = Field(..., alias="_id")
    profile_created_at: datetime = Field(...)

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {ObjectId: str}


# ---------------------------
# Events
# ---------------------------
class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    tags: List[str] = []  # e.g. ["hackathon", "networking"]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class EventDB(EventCreate):
    id: PyObjectId = Field(..., alias="_id")
    created_at: datetime = Field(...)

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {ObjectId: str}


# ---------------------------
# Clubs
# ---------------------------
class ClubCreate(BaseModel):
    name: str
    description: Optional[str] = None
    meeting_times: Optional[str] = None
    tags: List[str] = []
    contact_email: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ClubDB(ClubCreate):
    id: PyObjectId = Field(..., alias="_id")
    created_at: datetime = Field(...)

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {ObjectId: str}


# ---------------------------
# Attendances
# ---------------------------
class AttendanceCreate(BaseModel):
    user_id: PyObjectId
    event_id: PyObjectId
    scanned_at: Optional[datetime] = None
    # Optional inline feedback data (e.g., rating, comments)
    feedback: Optional[dict] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AttendanceDB(AttendanceCreate):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {ObjectId: str}


# ---------------------------
# Memberships
# ---------------------------
class MembershipCreate(BaseModel):
    user_id: PyObjectId
    club_id: PyObjectId
    joined_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MembershipDB(MembershipCreate):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {ObjectId: str}


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

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FeedbackDB(FeedbackCreate):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {ObjectId: str}


# ---------------------------
# Resources
# ---------------------------
class ResourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    contact_info: Optional[str] = None
    tags: List[str] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ResourceDB(ResourceCreate):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {ObjectId: str}
