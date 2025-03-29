from pydantic import BaseModel, Field
from datetime import datetime
from pyobjectid import PyObjectId
from bson import ObjectId


class AISummaryCreate(BaseModel):
    event_id: PyObjectId
    request: str
    response: str
    created_at: datetime = Field(...)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AISummaryDB(AISummaryCreate):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {ObjectId: str}
